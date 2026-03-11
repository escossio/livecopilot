const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');
const suggestionsEl = document.getElementById('suggestions');
const quickRepliesEl = document.getElementById('quick-replies');
const fillersEl = document.getElementById('fillers');
const termHintsEl = document.getElementById('term-hints');
const debugPanelEl = document.getElementById('debug-panel');
const knowledgeDebugEl = document.getElementById('knowledge-debug');

const form = document.getElementById('ingest-form');
const input = document.getElementById('mock-input');

const uiState = {
  wsEnabled: true,
  captureMode: 'mock',
  captureLive: false,
  wsConnected: false,
  knowledgeDebugEnabled: false
};

function setStatus(text, isOk) {
  statusEl.textContent = text;
  statusEl.classList.toggle('ok', Boolean(isOk));
}

function formatCaptureLabel() {
  if (uiState.captureLive) {
    return 'CAPTURA REAL';
  }
  if (uiState.captureMode && uiState.captureMode.toLowerCase() !== 'mock') {
    return `CAPTURA ${uiState.captureMode.toUpperCase()}`;
  }
  return 'MOCK';
}

function refreshStatus() {
  if (!uiState.wsEnabled) {
    setStatus(`MODO LOCAL · ${formatCaptureLabel()}`, true);
    return;
  }
  if (uiState.wsConnected) {
    setStatus(`CONECTADO · ${formatCaptureLabel()}`, true);
    return;
  }
  setStatus(`PRONTO · ${formatCaptureLabel()}`, true);
}

function renderList(el, items, formatter) {
  el.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = formatter ? formatter(item) : item;
    el.appendChild(li);
  });
}

function updateUI(snapshot) {
  renderList(transcriptEl, snapshot.transcript || [], (item) => `${item.speaker}: ${item.text}`);
  renderList(suggestionsEl, snapshot.suggestions || []);
  renderList(quickRepliesEl, snapshot.quick_replies || []);
  renderList(fillersEl, snapshot.fillers || []);
  renderList(termHintsEl, snapshot.term_hints || []);
  if (uiState.knowledgeDebugEnabled && snapshot.knowledge_debug && knowledgeDebugEl) {
    knowledgeDebugEl.textContent = JSON.stringify(snapshot.knowledge_debug, null, 2);
  }
}

function setDebugVisibility() {
  if (!debugPanelEl) return;
  debugPanelEl.classList.toggle('hidden', !uiState.knowledgeDebugEnabled);
}

async function sendMock(text) {
  const res = await fetch('/ingest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  const payload = await res.json();
  if (payload.snapshot) {
    updateUI(payload.snapshot);
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const value = input.value.trim();
  if (!value) return;
  sendMock(value);
  input.value = '';
});

function connectWS() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

  ws.onopen = () => {
    uiState.wsConnected = true;
    refreshStatus();
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
  };

  ws.onerror = () => {
    uiState.wsConnected = false;
    refreshStatus();
  };

  ws.onclose = () => {
    uiState.wsConnected = false;
    refreshStatus();
    setTimeout(connectWS, 1500);
  };
}

async function bootstrapStatus() {
  try {
    const res = await fetch('/status');
    if (!res.ok) throw new Error('status');
    const data = await res.json();
    uiState.wsEnabled = Boolean(data.ws_enabled);
    uiState.captureMode = data.capture_mode || 'mock';
    uiState.captureLive = Boolean(data.capture_live);
    uiState.knowledgeDebugEnabled = Boolean(data.knowledge_debug_enabled);
  } catch (err) {
    uiState.wsEnabled = false;
    uiState.knowledgeDebugEnabled = false;
  }
  setDebugVisibility();
  refreshStatus();
  if (uiState.wsEnabled) {
    connectWS();
  }
}

bootstrapStatus();
