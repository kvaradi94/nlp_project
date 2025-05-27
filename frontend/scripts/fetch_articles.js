function createArticleCard(article, id) {
    return `
        <div class="article-card">
            <div class="article-content">
                <h2 class="article-title" id="article-${id}-title">${article.title}</h2>
                <div class="pdf-link">
                    [
                    <a href="${article.url}" target="_blank" class="article-link" id="article-${id}-url">
                        pdf
                    </a>
                    ]
                </div>
                <p class="article-abstract" id="article-${id}-abstract">${article.abstract}</p>
                <div class="article-footer">
                    <p class="labels" id="labels-${id}">${article.keywords}<p>
                    <button class="ai-discussion-button" id="ai-discussion-button" onclick="openChat('${article.url}')">Discuss the paper with AI</button>
                </div>
            </div>
        </div>
    `;
}

document.getElementById('get-articles').addEventListener('click', fetchPaper);

async function fetchPaper() {
    var reqToLoad = document.getElementById("req-to-load");
    reqToLoad.innerHTML = maxNumOfArticlesSlider.value;

    const button = document.getElementById('get-articles');
    button.innerText = "Loading...";
    button.disabled = true;
    var loadedStatus = document.getElementById("processing-status");
    loadedStatus.hidden = false;
    var articles = document.getElementById("articles");
    articles.innerHTML = "";

    try {
        // get status of the processed papers
        const eventSource = new EventSource('http://127.0.0.1:5000/status');
        eventSource.onmessage = (e) => {
            var loaded = document.getElementById("loaded");
            loaded.innerText = e.data;
        };

        const topicSelect = document.getElementById("topic-select");
        const summarizerModelSelect = document.getElementById("summarizer-select")
        const embeddingModelSelect = document.getElementById("embedding-select")
        const llmModelSelect = document.getElementById("llm-select")
        const titleInput = document.getElementById("title-input");
        
        const response = await fetch('http://127.0.0.1:5000/?max=' + maxNumOfArticlesSlider.value + 
            "&days=" + lastXDaysSlider.value + "&cat=" + topicSelect.value + "&ti=" + titleInput.value +
            "&sum_m=" + summarizerModelSelect.value + "&emb_m=" + embeddingModelSelect.value +
            "&llm_m=" + llmModelSelect.value);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const container = document.getElementById('articles');
        container.innerHTML = "";

        for (i = 0; i < Object.keys(data).length; i++) {
            container.innerHTML += createArticleCard(data[i], i);

            const p = document.getElementById('labels-' + i);
            const words = p.textContent.split(' ');

            const baseColorCount = 12;
            const colors = generateDistinctColors(baseColorCount);
            shuffle(colors);

            p.innerHTML = words.map((word, index) => {
                
                return `<span class="label" style="color: ${color};">${word}</span>`;
            }).join(' ');
        }
        button.disabled = false;
        button.innerText = "GET ARTICLES";
        loadedStatus.hidden = true;
        eventSource.close();
    } catch (error) {
        alert('Error fetching paper: ' + error.message);
        button.disabled = false;
        button.innerText = "GET ARTICLES";
        loadedStatus.hidden = true;
        eventSource.close();
    }
}

function generateDistinctColors(count) {
    const colors = [];
    const saturation = 70;
    const lightness = 60;
    for (let i = 0; i < count; i++) {
        const hue = Math.floor((360 / count) * i);
        colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
    }
    return colors;
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function getKeyByValue(object, value) {
    return Object.keys(object).find(key => object[key] === value);
}

function openChat(pdfUrl) {
    const encodedUrl = encodeURIComponent(pdfUrl);
    window.open(`ai_chat.html?pdf=${encodedUrl}`, '_blank');
}