import requests
import xml.etree.ElementTree as ET
import json
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import time
from PyPDF2 import PdfReader

from transformers import pipeline

from keybert import KeyBERT
from io import BytesIO
from llama_index.core import Settings
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory.chat_memory_buffer import ChatMemoryBuffer
from llama_index.llms.huggingface import HuggingFaceLLM
import base64
import webbrowser
import os
import urllib.request

summarizer_model = "facebook/bart-large-cnn"
embedding_model = "sentence-transformers/all-mpnet-base-v2"
llm_model = "Gensyn/Qwen2.5-1.5B-Instruct"

script_dir = os.path.dirname(os.path.abspath(__file__))
html_file = "../../frontend/index.html"
file_path = os.path.join(script_dir, html_file)
num_of_processed_papers = 0
TOP_N_KEYWORD = 3
HARD_LIMIT_MAX_RESULT = 100
HARD_LIMIT_MAX_DAYS = 30
HTTP_OK = 200
chat_engine = None

webbrowser.open(f"file://{file_path}")

app = Flask(__name__)
CORS(app)

@app.route('/status')
def status():
    def generate():
        while(True):
            global num_of_processed_papers
            # SSE format requires "data:" prefix and double newline
            yield f"data: {num_of_processed_papers}\n\n"
            time.sleep(0.5)

    response = Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

    return response

@app.route('/download', methods=['GET'])
def download():
    if os.path.exists("paper.pdf"):
        os.remove("paper.pdf")
        print("Old paper.pdf was existed, now removed.")

    pdf_url_base64 = request.args.get('pdf_url', type=str)
    pdf_url = base64.b64decode(pdf_url_base64).decode("utf-8")
    print(f"PDF to download: {pdf_url}")
    urllib.request.urlretrieve(pdf_url, "paper.pdf")
    print(f"{pdf_url} is downloaded")

    return {"message": "OK"}, 200

@app.route('/learn', methods=['GET'])
def learn():
    pdf_url = request.args.get('pdf_url', type=str) 
    print(f"PDF to load: {pdf_url}")

    response = requests.get(pdf_url)

    with BytesIO(response.content) as pdf_buffer:
        reader = PdfReader(pdf_buffer)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

    pdf_len = len(text)
    print(f"Size of the loaded PDF content: {pdf_len}")
    chunks = []
    chunk_size_by_words = 150

    text_split = text.split(" ") 
    for i in range(0, len(text_split), chunk_size_by_words):
        chunk = " ".join(text_split[i:i + chunk_size_by_words])
        chunks.append(Document(text=chunk))

    # Initialize the embedding model
    print(f"Creating vectore database with {embedding_model} embedding model")
    Settings.llm = None
    Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_model)

    # Create the VectorStoreIndex
    vectore_store_index = VectorStoreIndex.from_documents(chunks, show_progress=True, insert_batch_size=len(chunks))
    print("Vectore database is created")

    print(f"Loading LLM: {llm_model}")
    llm = HuggingFaceLLM(
    model_name=llm_model,
    tokenizer_name=llm_model,
    context_window=20480,
    max_new_tokens=2560,
    device_map="auto",
    # These parameters influence the randomness and creativity of the model's answer.
    generate_kwargs={"temperature": 0.9, "top_p": 0.8, "repetition_penalty": 1.05, "do_sample": True},
    )

    Settings.llm = llm
    print("LLM is loaded.")

    print("Creating chat engine.")
    global chat_engine
    # Create the chat engine which is responsible for the discussion with the AI agent
    chat_engine = vectore_store_index.as_chat_engine(
        # Configure the chat engine to use the vectore database for the answers
        chat_mode="context",
        memory=ChatMemoryBuffer.from_defaults(token_limit=32000),
        # Configure system prompt to define the behaviour of the agent
        system_prompt=(
            "You are a professior who helps understand the given scientific paper. You only answer based on the given paper."
        )
    )
    print("Chat engine is created")

    return "OK"

@app.route('/chat', methods=['POST'])
def chat():
    question = request.json.get('message', '')
    print(f"Recieved question: {question}")

    start = datetime.now()

    global chat_engine
    response = chat_engine.chat(question)
    answer = response.response

    end = datetime.now()
    elapsed_time = end - start
    print(f"Elapsed time: {elapsed_time}")

    print(f"The answer for that question: {answer}")

    # Encode the final answer to Base64
    string_bytes = answer.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    
    return jsonify({'response': base64_string})

@app.route('/', methods=['GET'])
def get_paper():
    max_result = request.args.get('max', default=1, type=int) 
    timeframe_days = request.args.get('days', default=7, type=int) 
    category = request.args.get('cat', type=str) 
    title = request.args.get('ti', type=str)
    sum_model_req_param = request.args.get('sum_m', type=str) 
    embedding_model_req_param = request.args.get('emb_m', type=str) 
    llm_model_req_param = request.args.get('llm_m', type=str) 

    print(f"GET request recieved, max: {max_result}, days: {timeframe_days}, cat: {category}, ti: {title}, sum_m: {sum_model_req_param}, emb_m: {embedding_model_req_param}, llm_m: {llm_model_req_param}")

    global summarizer_model
    summarizer_model = sum_model_req_param
    global embedding_model
    embedding_model = embedding_model_req_param
    global llm_model
    llm_model = llm_model_req_param

    CONTENT = dict()

    if max_result > HARD_LIMIT_MAX_RESULT:
        max_result = HARD_LIMIT_MAX_RESULT

    if timeframe_days > HARD_LIMIT_MAX_DAYS:
        timeframe_days = HARD_LIMIT_MAX_DAYS

    end_date = datetime.now(timezone.utc) 
    start_date = end_date - timedelta(days=timeframe_days)
    # Format the date for ArXiv API: YYYYMMDD
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    # Get the top MAX_RESULT most relevant artical via arXiv API
    url = 'http://export.arxiv.org/api/query'
    params = {
        'search_query': f'cat:{category} AND ti:"{title}" AND submittedDate:[{start_str} TO {end_str}]',
        'sortBy': 'relevance',
        'sortOrder': 'descending',
        'max_results': max_result
    }

    response = requests.get(url, params=params)

    if response.status_code != HTTP_OK:
        print(f"Error during arXiv api call: {response.status_code}")
        return

    # the response is an XML content, parsing the xml
    root = ET.fromstring(response.content)
    entries = root.findall('{http://www.w3.org/2005/Atom}entry')

    print(f"Loading {summarizer_model} summarization model")
    summarizer = pipeline("summarization", model=summarizer_model)
    print(f"{summarizer_model} summarization model is loaded")

    print("Loading KeyBERT")
    kw_model = KeyBERT()
    print("KeyBERT is loaded")

    counter = 0

    if not entries:
        print("No results for the recieved searching criteria.")
    else:
        for entry in entries:
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            abstract_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
            id_elem = entry.find('{http://www.w3.org/2005/Atom}id')

            title = title_elem.text.strip() if title_elem is not None else "Unknown"
            abstract = abstract_elem.text.strip().replace('\n', ' ') if abstract_elem is not None else "Unknown"
            paper_id = id_elem.text.strip().split('/')[-1] if id_elem is not None else "Unknown"
            pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

            summary = abstract
            if (abstract != "Unknown"):
                summary = summarizer(abstract)[0]['summary_text']

                keywords = kw_model.extract_keywords(abstract, top_n=TOP_N_KEYWORD, use_mmr=True)
                keywords_only = [kw[0] for kw in keywords]
                keywords_formatted = ' '.join(keywords_only) 

            CONTENT[counter] = {"title": title, "abstract": summary, "url": pdf_url, "keywords": keywords_formatted}
            counter += 1
            global num_of_processed_papers
            num_of_processed_papers = counter
            print(f"{counter} article is processed.")

    json_data = json.dumps(CONTENT, ensure_ascii=False)

    time.sleep(0.6)
    num_of_processed_papers = 0

    return json_data

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
