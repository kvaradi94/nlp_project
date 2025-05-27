document.querySelectorAll('.radio-option').forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.checked) {
            setTopicsList(topics[this.id]);
        }
    });
});

function setTopicsList(topics) {
    const select = document.getElementById('topic-select');
    select.innerHTML = '';

    for (const [value, text] of Object.entries(topics)) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;

        if (value === '*') {
            option.selected = true;
        }

        select.appendChild(option);
    }
}

setTopicsList(cs_topics);
