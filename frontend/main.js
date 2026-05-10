const API_BASE = 'http://localhost:3001/api';

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const ideationCol = document.getElementById('col-ideation');

let state = {
    messages: [],
    gusti: []
};

// --- CHAT LOGIC ---

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, 'user');
    chatInput.value = '';

    // Typing indicator
    const aiMsgId = addMessage('Sto analizzando i cataloghi per trovare i best match...', 'ai');

    try {
        const response = await fetch(`${API_BASE}/match-concept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ concept: text })
        });
        const data = await response.json();

        updateAiMessage(aiMsgId, formatAiResponse(text, data));
        
        // Automatically create a card in the Kanban
        createGustoCard(text, data);

    } catch (err) {
        console.error(err);
        updateAiMessage(aiMsgId, "Scusa Chef, ho avuto un problema nel collegarmi al database. Verifica che il server sia attivo.");
    }
}

function addMessage(text, type) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.innerText = text;
    msgDiv.id = 'msg-' + Date.now();
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv.id;
}

function updateAiMessage(id, html) {
    const msgDiv = document.getElementById(id);
    if (msgDiv) {
        msgDiv.innerHTML = html;
    }
}

function formatAiResponse(concept, data) {
    let html = `Ottima idea! Per il gusto <strong>"${concept}"</strong>, ecco cosa ho trovato nei cataloghi:<br><br>`;
    
    if (data.paste.length > 0) {
        html += `<strong>Paste consigliate:</strong><ul>`;
        data.paste.forEach(p => html += `<li>${p.name} (${p.manufacturer_name})</li>`);
        html += `</ul>`;
    }
    
    if (data.variegature.length > 0) {
        html += `<strong>Variegature ideali:</strong><ul>`;
        data.variegature.forEach(v => html += `<li>${v.name} (${v.manufacturer_name})</li>`);
        html += `</ul>`;
    }

    if (data.inclusioni.length > 0) {
        html += `<strong>Inclusioni:</strong><ul>`;
        data.inclusioni.forEach(i => html += `<li>${i.name} (${i.manufacturer_name})</li>`);
        html += `</ul>`;
    }

    html += `<br>Ho aggiunto una bozza alla tua Kanban. Vuoi approfondire uno di questi prodotti?`;
    return html;
}

// --- KANBAN LOGIC ---

function createGustoCard(title, data) {
    const card = document.createElement('div');
    card.className = 'gusto-card';
    
    let tagsHtml = '';
    if (data.paste.length > 0) tagsHtml += `<span class="tag tag-pasta">${data.paste[0].name}</span>`;
    if (data.variegature.length > 0) tagsHtml += `<span class="tag tag-variegato">${data.variegature[0].name}</span>`;
    if (data.inclusioni.length > 0) tagsHtml += `<span class="tag tag-inclusione">${data.inclusioni[0].name}</span>`;

    card.innerHTML = `
        <div class="card-title">${title}</div>
        <div class="ingredient-tags">
            ${tagsHtml}
        </div>
    `;
    
    ideationCol.appendChild(card);
}

// --- EVENTS ---

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
