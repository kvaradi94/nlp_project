var pdf_url = "";

requestPdfDownload();
loadPdf();
learn();

const chatLog = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

function appendMessage(message, sender) {
    const messageElem = document.createElement("p");
    const formattedMessage = message.replace(/\n/g, "<br>");
    messageElem.innerHTML = formattedMessage;
    messageElem.className = sender === "user" ? "user-message" : "bot-message";
    chatLog.appendChild(messageElem);
    chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage() {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, "user");
    chatInput.value = "";

    sendBtn.disabled = true;
    sendBtn.style.opacity = "50%";

    const loadingAnimation = document.getElementById("loading-animation");
    loadingAnimation.style.display = "block";

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        appendMessage(atob(data.response), "bot");
    } catch (error) {
        appendMessage("Error: Unable to connect to the server.", "bot");
    } finally {
        loadingAnimation.style.display = "none";
        sendBtn.disabled = false;
        sendBtn.style.opacity = "100%";
    }
}

async function initialConversation() {
    const userMessage = "Explain what the given paper is about and what are the presented results."

    chatInput.value = "";

    sendBtn.disabled = true;
    sendBtn.style.opacity = "50%";

    const loadingAnimation = document.getElementById("loading-animation");
    loadingAnimation.style.display = "block";

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        appendMessage(atob(data.response), "bot");
    } catch (error) {
        appendMessage("Error: Unable to connect to the server.", "bot");
    } finally {
        loadingAnimation.style.display = "none";
        sendBtn.disabled = false;
        sendBtn.style.opacity = "100%";
    }
}

sendBtn.addEventListener("click", sendMessage);

chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !sendBtn.disabled) {
        sendMessage();
    }
});

async function learn() {
    const response = await fetch('http://127.0.0.1:5000/learn?pdf_url=' + pdf_url);
    if (!response.ok) {
        alert("Response was learning was not OK");
    } else {
        loadPdf();
        const opacitySliderContainer = document.getElementById("opacity-slider-container");
        opacitySliderContainer.hidden = false;
        initialConversation();
    }
}

async function requestPdfDownload() {
    const urlParams = new URLSearchParams(window.location.search);
    const pdfUrl = urlParams.get('pdf');
    const decodedPdfUrl = decodeURIComponent(pdfUrl);
    pdf_url = decodedPdfUrl;
    const pdf_url_base64 = btoa(pdf_url)
    await fetch('http://127.0.0.1:5000/download?pdf_url=' + pdf_url_base64);
}

function loadPdf() {
    const containerPaper = document.getElementById("container-paper");
    containerPaper.innerHTML = '<iframe class="pdf-frame" id="pdf-frame" src="../backend/python/paper.pdf" style="border: none;"></iframe>'
    const slider = document.getElementById('opacity-slider');
    const pdfFrame = document.getElementById('pdf-frame');

    slider.addEventListener('input', function () {
        const opacityValue = this.value;
        pdfFrame.style.opacity = opacityValue;
    });
}

