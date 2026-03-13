const statusEl = document.getElementById('status');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatSubmit = document.getElementById('chat-submit');
const chatFeedback = document.getElementById('chat-feedback');
const modeSelect = document.getElementById('mode-select');
const voiceStartBtn = document.getElementById('voice-start');
const voiceStopBtn = document.getElementById('voice-stop');
const voiceMetaEl = document.getElementById('voice-meta');
const interactionLogEl = document.getElementById('interaction-log');
const latestAnswerEl = document.getElementById('latest-answer');
const responseBulletsEl = document.getElementById('response-bullets');
const interactionStatusEl = document.getElementById('interaction-status');
const backendContextEl = document.getElementById('backend-context');
const remoteAudioEl = document.getElementById('remote-audio');
const debugPanelEl = document.getElementById('debug-panel');
const knowledgeDebugEl = document.getElementById('knowledge-debug');

const uiState = {
  statusText: 'inicializando',
  chatBusy: false,
  wsEnabled: true,
  wsConnected: false,
  captureMode: 'mock',
  captureLive: false,
  knowledgeDebugEnabled: false,
  realtimeEnabled: false,
  realtimeReady: false,
  realtimeProvider: 'openai_realtime',
  realtimeModel: '',
  realtimeVoice: '',
  conversationId: '',
  interactionLog: [],
  latestAnswer: '',
  latestBullets: [],
  latestContext: {},
  latestStatus: [],
  voice: {
    state: 'idle',
    transport: 'webrtc',
    sessionId: '',
    sessionStartedAt: '',
    pc: null,
    dc: null,
    localStream: null,
    assistantTranscript: '',
    diagnostics: {
      secureContext: false,
      mediaDevicesAvailable: false,
      getUserMediaAvailable: false,
      rtcPeerConnectionAvailable: false,
    },
  },
};

function setStatus(text, isOk) {
  statusEl.textContent = text;
  statusEl.classList.toggle('ok', Boolean(isOk));
}

function refreshTopStatus() {
  if (uiState.chatBusy) {
    setStatus('consultando livecopilot por texto', true);
    return;
  }
  if (uiState.voice.state === 'connecting') {
    setStatus('conectando voz como entrada do livecopilot', true);
    return;
  }
  if (uiState.voice.state === 'live') {
    setStatus('voz ativa para consultar o livecopilot', true);
    return;
  }
  if (uiState.realtimeEnabled && uiState.realtimeReady) {
    setStatus('pronto para consultar por texto ou voz', true);
    return;
  }
  setStatus('pronto para consulta por texto', true);
}

function renderList(el, items) {
  el.innerHTML = '';
  (items || []).forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    el.appendChild(li);
  });
}

function pushInteraction(role, text) {
  const clean = String(text || '').trim();
  if (!clean) return;
  uiState.interactionLog.push(`${role}: ${clean}`);
  uiState.interactionLog = uiState.interactionLog.slice(-20);
  renderList(interactionLogEl, uiState.interactionLog);
}

function renderVoiceMeta() {
  const diagnostics = uiState.voice.diagnostics || {};
  const rows = [
    `estado: ${uiState.voice.state}`,
    `sessao: ${uiState.voice.sessionId || 'nao iniciada'}`,
    `modelo: ${uiState.realtimeModel || 'indefinido'}`,
    `voz: ${uiState.realtimeVoice || 'indefinida'}`,
    `transporte: ${uiState.voice.transport}`,
    `secure_context: ${String(Boolean(diagnostics.secureContext))}`,
    `media_devices: ${String(Boolean(diagnostics.mediaDevicesAvailable))}`,
    `get_user_media: ${String(Boolean(diagnostics.getUserMediaAvailable))}`,
  ];
  renderList(voiceMetaEl, rows);
}

function renderInteractionStatus() {
  renderList(interactionStatusEl, uiState.latestStatus);
}

function renderBackendContext() {
  const context = uiState.latestContext || {};
  const rows = [
    `backend: ${context.search_backend || context.backend || 'n/a'}`,
    `resultados: ${context.result_count ?? 'n/a'}`,
    `contexto_usado: ${String(Boolean(context.context_used))}`,
    `buffer_chunks: ${context.buffer_chunks ?? 0}`,
    `buffer_chars: ${context.buffer_chars ?? 0}`,
  ];
  if (context.source_titles && context.source_titles.length) {
    context.source_titles.slice(0, 2).forEach((item, idx) => {
      rows.push(`fonte_${idx + 1}: ${item}`);
    });
  }
  renderList(backendContextEl, rows);
}

function updateAnswer(answer, bullets) {
  uiState.latestAnswer = String(answer || '').trim();
  uiState.latestBullets = Array.isArray(bullets) ? bullets : [];
  latestAnswerEl.textContent = uiState.latestAnswer || 'Nenhuma resposta ainda.';
  renderList(responseBulletsEl, uiState.latestBullets);
}

function setChatFeedback(text, isError = false) {
  chatFeedback.textContent = text;
  chatFeedback.classList.toggle('error', Boolean(isError));
}

function setChatBusy(next) {
  uiState.chatBusy = Boolean(next);
  chatSubmit.disabled = uiState.chatBusy;
  chatInput.disabled = uiState.chatBusy;
  modeSelect.disabled = uiState.chatBusy;
  refreshTopStatus();
}

async function sendTextMessage(text) {
  setChatBusy(true);
  setChatFeedback('Enviando consulta ao motor do Livecopilot...');
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        mode: modeSelect.value || 'generic',
        conversation_id: uiState.conversationId || undefined,
      }),
    });
    const payload = await res.json();
    if (!res.ok) {
      throw new Error(payload.error || 'falha no /api/chat');
    }
    uiState.conversationId = payload.conversation_id || uiState.conversationId;
    uiState.latestContext = payload.knowledge_context || {};
    uiState.latestStatus = [
      `canal: texto`,
      `motor: livecopilot`,
      `mode: ${payload.mode || 'generic'}`,
      `stage: ${payload.response_stage || 'final'}`,
      `readiness: ${payload.readiness || 'n/a'}`,
      `latencia_ms: ${payload.latency_ms ?? 'n/a'}`,
    ];
    pushInteraction('usuario', payload.input_text || text);
    pushInteraction('livecopilot', payload.answer || '');
    updateAnswer(payload.answer, payload.bullets);
    renderInteractionStatus();
    renderBackendContext();
    if (uiState.knowledgeDebugEnabled && payload.snapshot && payload.snapshot.knowledge_debug && knowledgeDebugEl) {
      knowledgeDebugEl.textContent = JSON.stringify(payload.snapshot.knowledge_debug, null, 2);
    }
    setChatFeedback('Resposta recebida do motor do Livecopilot.');
  } catch (err) {
    setChatFeedback(`Erro: ${err.message || 'falha inesperada'}`, true);
    uiState.latestStatus = ['canal: texto', 'erro: true'];
    renderInteractionStatus();
  } finally {
    setChatBusy(false);
  }
}

function resetVoiceTransport() {
  if (uiState.voice.dc) {
    try { uiState.voice.dc.close(); } catch (_) {}
  }
  if (uiState.voice.pc) {
    try { uiState.voice.pc.close(); } catch (_) {}
  }
  if (uiState.voice.localStream) {
    uiState.voice.localStream.getTracks().forEach((track) => track.stop());
  }
  if (remoteAudioEl) {
    remoteAudioEl.srcObject = null;
  }
  uiState.voice.pc = null;
  uiState.voice.dc = null;
  uiState.voice.localStream = null;
  uiState.voice.assistantTranscript = '';
}

function setVoiceState(state, extraStatus) {
  uiState.voice.state = state;
  voiceStartBtn.disabled = state === 'connecting' || state === 'live';
  voiceStopBtn.disabled = state !== 'connecting' && state !== 'live';
  if (extraStatus) {
    uiState.latestStatus = Array.isArray(extraStatus) ? extraStatus : [extraStatus];
    renderInteractionStatus();
  }
  renderVoiceMeta();
  refreshTopStatus();
}

function collectVoiceDiagnostics() {
  const nav = typeof navigator === 'object' && navigator ? navigator : null;
  const mediaDevices = nav && typeof nav.mediaDevices === 'object' ? nav.mediaDevices : null;
  return {
    secureContext: Boolean(window.isSecureContext),
    mediaDevicesAvailable: Boolean(mediaDevices),
    getUserMediaAvailable: Boolean(mediaDevices && typeof mediaDevices.getUserMedia === 'function'),
    rtcPeerConnectionAvailable: typeof window.RTCPeerConnection === 'function',
  };
}

function buildVoiceSupportMessage(diagnostics) {
  if (!diagnostics.rtcPeerConnectionAvailable) {
    return 'Seu navegador ou contexto atual nao suporta WebRTC para a trilha de voz.';
  }
  if (!diagnostics.secureContext) {
    return 'Seu navegador ou contexto atual nao disponibiliza captura de microfone. Para usar voz, abra a interface em HTTPS ou localhost.';
  }
  return 'Seu navegador ou contexto atual nao suporta captura de microfone. Para usar voz, abra a interface em navegador compativel com getUserMedia/WebRTC e libere a permissao de microfone.';
}

function describeVoiceError(err) {
  const errorName = String(err?.name || '').trim();
  if (errorName === 'NotAllowedError' || errorName === 'PermissionDeniedError') {
    return 'Acesso ao microfone negado. Libere a permissao do microfone no navegador para usar voz.';
  }
  if (errorName === 'NotFoundError' || errorName === 'DevicesNotFoundError') {
    return 'Nenhum microfone disponivel foi encontrado neste dispositivo.';
  }
  if (errorName === 'NotReadableError' || errorName === 'TrackStartError') {
    return 'Nao foi possivel acessar o microfone. Feche outros apps que possam estar usando o dispositivo e tente novamente.';
  }
  if (errorName === 'SecurityError') {
    return 'A captura de microfone nao esta disponivel neste contexto. Abra a interface em HTTPS ou localhost.';
  }
  return String(err?.message || 'falha realtime');
}

function handleUnsupportedVoiceEnvironment() {
  const diagnostics = collectVoiceDiagnostics();
  uiState.voice.diagnostics = diagnostics;
  resetVoiceTransport();
  const message = buildVoiceSupportMessage(diagnostics);
  setVoiceState('error', [
    'canal: voz',
    'erro: ambiente_sem_captura',
    `secure_context: ${String(Boolean(diagnostics.secureContext))}`,
    `media_devices: ${String(Boolean(diagnostics.mediaDevicesAvailable))}`,
    `get_user_media: ${String(Boolean(diagnostics.getUserMediaAvailable))}`,
  ]);
  setChatFeedback(message, true);
  console.warn('voice_unsupported_environment', diagnostics);
}

function extractEventText(event) {
  if (!event || typeof event !== 'object') return '';
  const directCandidates = [
    event.transcript,
    event.delta,
    event.text,
    event.output_text,
    event.response?.output_text,
  ];
  for (const value of directCandidates) {
    const clean = String(value || '').trim();
    if (clean) return clean;
  }
  const item = event.item || {};
  const itemCandidates = [
    item.transcript,
    item.text,
    item.content?.[0]?.transcript,
    item.content?.[0]?.text,
  ];
  for (const value of itemCandidates) {
    const clean = String(value || '').trim();
    if (clean) return clean;
  }
  return '';
}

function handleRealtimeEvent(event) {
  const type = String(event?.type || '').trim();
  if (!type) return;

  if (type === 'session.created' || type === 'session.updated') {
    uiState.latestStatus = [
      `canal: voz`,
      `evento: ${type}`,
      `fluxo: voz -> transcricao -> livecopilot`,
      `modelo: ${uiState.realtimeModel || 'n/a'}`,
    ];
    renderInteractionStatus();
    return;
  }

  if (type === 'input_audio_buffer.speech_started') {
    setVoiceState('live', ['canal: voz', 'evento: fala_detectada', 'estado: ouvindo para consultar']);
    return;
  }

  if (type === 'input_audio_buffer.speech_stopped') {
    uiState.latestStatus = ['canal: voz', 'evento: fala_finalizada', 'estado: aguardando transcricao/resposta'];
    renderInteractionStatus();
    return;
  }

  if (type === 'conversation.item.input_audio_transcription.completed') {
    const text = extractEventText(event);
    if (text) {
      pushInteraction('voz->consulta', text);
      uiState.latestStatus = ['canal: voz', 'evento: transcricao_final', 'fluxo: consulta enviada ao livecopilot'];
      renderInteractionStatus();
    }
    return;
  }

  if (type === 'response.output_audio_transcript.delta' || type === 'response.audio_transcript.delta') {
    const delta = extractEventText(event);
    if (delta) {
      uiState.voice.assistantTranscript += delta;
      updateAnswer(uiState.voice.assistantTranscript, uiState.latestBullets);
    }
    return;
  }

  if (type === 'response.output_audio_transcript.done' || type === 'response.audio_transcript.done') {
    const text = extractEventText(event) || uiState.voice.assistantTranscript;
    if (text) {
      uiState.voice.assistantTranscript = text;
      updateAnswer(text, uiState.latestBullets);
      pushInteraction('livecopilot', text);
    }
    uiState.latestStatus = ['canal: voz', 'evento: resposta_final', 'motor: livecopilot', 'estado: concluido'];
    renderInteractionStatus();
    return;
  }

  if (type === 'response.done') {
    const text = extractEventText(event);
    if (text && !uiState.voice.assistantTranscript) {
      uiState.voice.assistantTranscript = text;
      updateAnswer(text, uiState.latestBullets);
      pushInteraction('livecopilot', text);
    }
    return;
  }

  if (type === 'error') {
    const text = extractEventText(event) || String(event?.error?.message || 'erro realtime');
    setVoiceState('error', [`canal: voz`, `erro: ${text}`]);
  }
}

async function startVoiceSession() {
  if (!uiState.realtimeEnabled) {
    setChatFeedback('Realtime API desabilitada no backend.', true);
    return;
  }
  const diagnostics = collectVoiceDiagnostics();
  uiState.voice.diagnostics = diagnostics;
  if (!diagnostics.rtcPeerConnectionAvailable || !diagnostics.mediaDevicesAvailable || !diagnostics.getUserMediaAvailable) {
    handleUnsupportedVoiceEnvironment();
    return;
  }
  setVoiceState('connecting', ['canal: voz', 'estado: criando sessao']);
  try {
    const sessionRes = await fetch('/api/realtime/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: modeSelect.value || 'generic' }),
    });
    const sessionPayload = await sessionRes.json();
    if (!sessionRes.ok) {
      throw new Error(sessionPayload.error || 'falha ao criar sessao realtime');
    }

    const pc = new RTCPeerConnection();
    const dc = pc.createDataChannel('oai-events');
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((track) => pc.addTrack(track, stream));

    pc.ontrack = (event) => {
      if (remoteAudioEl) {
        remoteAudioEl.srcObject = event.streams[0];
      }
    };
    pc.onconnectionstatechange = () => {
      if (pc.connectionState === 'connected') {
        setVoiceState('live', ['canal: voz', 'estado: conectado', 'fluxo: voz pronta para consulta']);
      } else if (['failed', 'disconnected', 'closed'].includes(pc.connectionState)) {
        setVoiceState('idle', ['canal: voz', `estado: ${pc.connectionState}`]);
      }
    };
    dc.onmessage = (event) => {
      try {
        handleRealtimeEvent(JSON.parse(event.data));
      } catch (_) {
        // Ignora eventos nao parseaveis.
      }
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const sdpRes = await fetch(`${sessionPayload.webrtc_url}?model=${encodeURIComponent(sessionPayload.model)}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${sessionPayload.client_secret}`,
        'Content-Type': 'application/sdp',
      },
      body: offer.sdp,
    });
    const answerSdp = await sdpRes.text();
    if (!sdpRes.ok) {
      throw new Error(answerSdp || 'falha ao negociar WebRTC com a OpenAI');
    }
    await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });

    uiState.voice.pc = pc;
    uiState.voice.dc = dc;
    uiState.voice.localStream = stream;
    uiState.voice.sessionId = `rt-${String(sessionPayload.expires_at || Date.now())}`;
    uiState.voice.sessionStartedAt = new Date().toISOString();
    uiState.realtimeModel = sessionPayload.model || uiState.realtimeModel;
    uiState.realtimeVoice = sessionPayload.voice || uiState.realtimeVoice;
    renderVoiceMeta();
    setVoiceState('live', ['canal: voz', 'estado: fale agora', 'fluxo: falar em vez de digitar']);
  } catch (err) {
    resetVoiceTransport();
    const message = describeVoiceError(err);
    setVoiceState('error', [`canal: voz`, `erro: ${message}`]);
    setChatFeedback(`Erro de voz: ${message}`, true);
  }
}

function stopVoiceSession() {
  resetVoiceTransport();
  setVoiceState('idle', ['canal: voz', 'estado: encerrado']);
}

function connectWS() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

  ws.onopen = () => {
    uiState.wsConnected = true;
    refreshTopStatus();
  };

  ws.onerror = () => {
    uiState.wsConnected = false;
    refreshTopStatus();
  };

  ws.onclose = () => {
    uiState.wsConnected = false;
    refreshTopStatus();
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
    uiState.realtimeEnabled = Boolean(data.realtime_api_enabled);
    uiState.realtimeReady = Boolean(data.realtime_api_enabled) && Boolean(data.realtime_api_key_present);
    uiState.realtimeProvider = data.realtime_api_provider || 'openai_realtime';
    uiState.realtimeModel = data.realtime_api_model || '';
    uiState.realtimeVoice = data.realtime_api_voice || '';
    if (uiState.knowledgeDebugEnabled && debugPanelEl) {
      debugPanelEl.classList.remove('hidden');
    }
  } catch (_) {
    uiState.wsEnabled = false;
    uiState.realtimeEnabled = false;
  }
  uiState.voice.diagnostics = collectVoiceDiagnostics();
  renderVoiceMeta();
  uiState.latestStatus = [
    `capture_mode: ${uiState.captureMode}`,
    `motor: livecopilot`,
    `realtime: ${uiState.realtimeReady ? 'ready' : 'unavailable'}`,
    `provider: ${uiState.realtimeProvider}`,
  ];
  renderInteractionStatus();
  renderBackendContext();
  refreshTopStatus();
  if (uiState.wsEnabled) {
    connectWS();
  }
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;
  await sendTextMessage(text);
  chatInput.value = '';
});

voiceStartBtn.addEventListener('click', async () => {
  await startVoiceSession();
});

voiceStopBtn.addEventListener('click', () => {
  stopVoiceSession();
});

bootstrapStatus();
