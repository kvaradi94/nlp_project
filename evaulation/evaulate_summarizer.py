from transformers import pipeline
from datasets import load_dataset
from evaluate import load
from tqdm import tqdm

ITERATION = 1000

dataset = load_dataset("cnn_dailymail", "3.0.0")["test"]
dataset_test = dataset.select(range(ITERATION)) if len(dataset) > ITERATION else dataset

# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

references = dataset_test["highlights"]

predictions = []
for article in tqdm(dataset_test["article"], desc="Summarizing articles"):
    summary = summarizer(article, max_length=130, min_length=30)[0]["summary_text"]
    predictions.append(summary)

rouge = load("rouge")
results = rouge.compute(predictions=predictions, references=references)
print(results)

