const apiUrl = 'http://localhost:5000/chat';
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const statusLine = document.getElementById('status-line');
const newChatBtn = document.getElementById('new-chat-btn');
const showTopicsBtn = document.getElementById('show-topics-btn');
const topicButtons = document.querySelectorAll('.topic-btn');

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    sendMessage();
  }
});
newChatBtn.addEventListener('click', clearChat);
showTopicsBtn.addEventListener('click', () => sendText('topics'));
topicButtons.forEach(button => {
  button.addEventListener('click', () => sendTopic(button.dataset.topic));
});

// Tool buttons
const sdToolBtn = document.getElementById('sd-tool-btn');
const ppfToolBtn = document.getElementById('ppf-tool-btn');
const priceGameBtn = document.getElementById('price-game-btn');

sdToolBtn && sdToolBtn.addEventListener('click', () => showTool('sd-tool'));
ppfToolBtn && ppfToolBtn.addEventListener('click', () => showTool('ppf-tool'));
priceGameBtn && priceGameBtn.addEventListener('click', () => showTool('price-game'));

// Load Chart.js dynamically
function loadChartJs(callback) {
  if (window.Chart) return callback();
  const s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/chart.js';
  s.onload = callback;
  document.head.appendChild(s);
}

function showTool(id) {
  document.querySelectorAll('.tool-card').forEach(el => el.classList.add('hidden'));
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('hidden');
  if (id === 'sd-tool') initSupplyDemandTool();
  if (id === 'ppf-tool') initPPFTool();
  if (id === 'price-game') initPriceGame();
}

// --- Supply & Demand tool ---
let sdChart = null;
function initSupplyDemandTool() {
  loadChartJs(() => {
    const ctx = document.getElementById('sd-chart').getContext('2d');
    if (sdChart) return updateSDChart();

    const labels = Array.from({length: 41}, (_, i) => i);
    sdChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Demand', data: [], borderColor: '#c026d3', fill: false },
          { label: 'Supply', data: [], borderColor: '#ff7ab6', fill: false },
          { label: 'Equilibrium', data: [], pointStyle: 'cross', showLine: false, borderColor: '#4d1a42' }
        ]
      },
      options: { responsive: true, maintainAspectRatio: true }
    });

    ['d0','d1','s0','s1'].forEach(id => document.getElementById(id).addEventListener('input', updateSDChart));
    updateSDChart();
  });
}

function updateSDChart() {
  const d0 = +document.getElementById('d0').value;
  const d1 = +document.getElementById('d1').value;
  const s0 = +document.getElementById('s0').value;
  const s1 = +document.getElementById('s1').value;

  const labels = sdChart.data.labels;
  const demand = labels.map(p => Math.max(0, Math.round(d0 - d1 * p)));
  const supply = labels.map(p => Math.max(0, Math.round(s0 + s1 * p)));

  sdChart.data.datasets[0].data = demand;
  sdChart.data.datasets[1].data = supply;

  // equilibrium: d0 - d1*p = s0 + s1*p
  const p_eq = (d0 - s0) / (d1 + s1);
  const q_eq = Math.max(0, Math.round(d0 - d1 * p_eq));
  sdChart.data.datasets[2].data = [{x: Math.round(p_eq), y: q_eq}];
  sdChart.update();

  document.getElementById('sd-info').innerText = `Equilibrium price ~ ${p_eq.toFixed(2)}, quantity ~ ${q_eq}`;
}

// --- PPF tool ---
let ppfChart = null;
function initPPFTool() {
  loadChartJs(() => {
    const ctx = document.getElementById('ppf-chart').getContext('2d');
    if (ppfChart) return updatePPFChart();
    ppfChart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [{ label: 'PPF', data: [], borderColor: '#8b1e64', fill: true, backgroundColor: 'rgba(255,230,240,0.6)' }] },
      options: { responsive: true, maintainAspectRatio: true, scales: { x: { title: { display: true, text: 'Good A' } }, y: { title: { display: true, text: 'Good B' } } } }
    });

    ['ppf-r','ppf-a','ppf-b'].forEach(id => document.getElementById(id).addEventListener('input', updatePPFChart));
    updatePPFChart();
  });
}

function updatePPFChart() {
  const R = +document.getElementById('ppf-r').value;
  const a = +document.getElementById('ppf-a').value;
  const b = +document.getElementById('ppf-b').value;

  const maxA = Math.round(R / a);
  const maxB = Math.round(R / b);
  const points = [];
  for (let x = 0; x <= maxA; x++) {
    const y = Math.max(0, Math.round((R - a * x) / b));
    points.push({x, y});
  }
  ppfChart.data.datasets[0].data = points;
  ppfChart.update();

  document.getElementById('ppf-info').innerText = `Max Good A ~ ${maxA}, Max Good B ~ ${maxB}`;
}

// --- Price control game ---
function initPriceGame() {
  const pcType = document.getElementById('pc-type');
  const pcPrice = document.getElementById('pc-price');
  pcType.addEventListener('change', updatePriceGame);
  pcPrice.addEventListener('input', updatePriceGame);
  updatePriceGame();
}

function updatePriceGame() {
  // Use current SD tool values or defaults
  const d0 = document.getElementById('d0') ? +document.getElementById('d0').value : 120;
  const d1 = document.getElementById('d1') ? +document.getElementById('d1').value : 3;
  const s0 = document.getElementById('s0') ? +document.getElementById('s0').value : 10;
  const s1 = document.getElementById('s1') ? +document.getElementById('s1').value : 2;

  const p_eq = (d0 - s0) / (d1 + s1);
  const q_eq = Math.max(0, Math.round(d0 - d1 * p_eq));

  const pcType = document.getElementById('pc-type').value;
  const pcPrice = +document.getElementById('pc-price').value;

  let info = `Market equilibrium price ~ ${p_eq.toFixed(2)}, quantity ~ ${q_eq}. `;
  if (pcType === 'none') info += 'No price control applied.';
  else if (pcType === 'ceiling') {
    if (pcPrice < p_eq) {
      const qd = Math.max(0, Math.round(d0 - d1 * pcPrice));
      const qs = Math.max(0, Math.round(s0 + s1 * pcPrice));
      info += `Ceiling binds. At price ${pcPrice}, quantity demanded ${qd}, quantity supplied ${qs}. Shortage ${qd - qs}.`;
    } else info += 'Ceiling does not bind; market clears at equilibrium.';
  } else if (pcType === 'floor') {
    if (pcPrice > p_eq) {
      const qd = Math.max(0, Math.round(d0 - d1 * pcPrice));
      const qs = Math.max(0, Math.round(s0 + s1 * pcPrice));
      info += `Floor binds. At price ${pcPrice}, quantity demanded ${qd}, quantity supplied ${qs}. Surplus ${qs - qd}.`;
    } else info += 'Floor does not bind; market clears at equilibrium.';
  }

  document.getElementById('pc-info').innerText = info;
}

window.addEventListener('load', () => {
  appendMessage('bot', 'Hello. Ask me about economics topics or click a topic below to learn more.');
});

function sendTopic(topic) {
  if (!topic) return;
  sendText(`Tell me about ${topic}`);
}

function sendMessage() {
  const message = userInput.value.trim();
  if (message === '') return;
  sendText(message);
}

function sendText(text) {
  appendMessage('user', text);
  userInput.value = '';
  setStatus('Sending…');

  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: text }),
  })
    .then(async response => {
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      appendMessage('bot', data.response || 'Sorry, I did not receive a valid response.');
      setStatus('Ready');
    })
    .catch(error => {
      console.error('Error:', error);
      appendMessage('bot', 'Sorry, something went wrong. Ensure the backend is running on http://localhost:5000.');
      setStatus('Error connecting');
    });
}

function appendMessage(sender, text) {
  const msg = document.createElement('div');
  msg.classList.add('message', `${sender}-message`);
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function clearChat() {
  chatBox.innerHTML = '';
  appendMessage('bot', 'Chat cleared. Ask a new question or choose a topic above.');
  setStatus('Ready');
}

function setStatus(message) {
  statusLine.textContent = message;
}
