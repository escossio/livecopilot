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
const tutorQuickRepliesEl = document.getElementById('tutor-quick-replies');
const interactionStatusEl = document.getElementById('interaction-status');
const backendContextEl = document.getElementById('backend-context');
const remoteAudioEl = document.getElementById('remote-audio');
const backendAudioEl = document.getElementById('backend-audio');
const debugPanelEl = document.getElementById('debug-panel');
const knowledgeDebugEl = document.getElementById('knowledge-debug');

const MIN_SILENCE_BEFORE_SUBMIT_MS = 220;
const MIN_SILENCE_GUARD_DELAY_MS = 40;

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
  latestTutorOptions: [],
  latestContext: {},
  latestStatus: [],
  interactionDedup: {},
  voice: {
    state: 'idle',
    transport: 'webrtc',
    sessionId: '',
    sessionStartedAt: '',
    conversationId: '',
    lastEvent: '',
    lastEventAt: '',
    lastBackendStatus: '',
    lastError: '',
    sessionTraceDir: '',
    pc: null,
    dc: null,
    localStream: null,
    assistantTranscript: '',
    requestInFlight: false,
    lastSubmittedTranscript: '',
    lastGreetingNormalized: '',
    greetingResponseLocked: false,
    lastGreetingNormalizedAt: 0,
    greetingEquivalentDuplicateSuppressed: false,
    pendingTranscript: '',
    lastVoiceOutputStatus: '',
    stopReason: '',
    stopDetail: '',
    stopRequestedAt: '',
    transcriptDedupToken: 1,
    autoStopLogged: false,
    backendAudioObjectUrl: '',
    backendAudioPrimed: false,
    pendingTranscriptGuard: '',
    pendingTranscriptGuardTimer: null,
    diagnostics: {
      secureContext: false,
      mediaDevicesAvailable: false,
      getUserMediaAvailable: false,
      rtcPeerConnectionAvailable: false,
    },
    timing: {
      turnStartedAtMs: 0,
      transcriptionCompletedAtMs: 0,
      backendRequestSentAtMs: 0,
      backendResponseReceivedAtMs: 0,
      voiceOutputReceivedAtMs: 0,
      playRequestedAtMs: 0,
      playStartedAtMs: 0,
      lastSpeechStoppedAtMs: 0,
    },
  },
};
uiState.interactionDedup['voice-transcript'] = { normalized: '', token: uiState.voice.transcriptDedupToken };

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

function renderTutorQuickReplies(options, context = {}) {
  if (!tutorQuickRepliesEl) return;
  const tutorModeUsed = Boolean(context?.tutor_mode_used);
  const cleanOptions = Array.isArray(options)
    ? options.map((item) => String(item || '').trim()).filter(Boolean).slice(0, 4)
    : [];
  tutorQuickRepliesEl.innerHTML = '';
  tutorQuickRepliesEl.classList.toggle('hidden', !(tutorModeUsed && cleanOptions.length));
  if (!(tutorModeUsed && cleanOptions.length)) {
    return;
  }
  const label = document.createElement('div');
  label.className = 'tutor-quick-replies-label';
  label.textContent = 'Próximo passo';
  tutorQuickRepliesEl.appendChild(label);
  const chips = document.createElement('div');
  chips.className = 'tutor-quick-replies-chips';
  cleanOptions.forEach((option) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'tutor-reply-chip';
    button.textContent = option;
    button.dataset.quickReply = option;
    button.addEventListener('click', () => {
      void sendTextMessage(option);
    });
    chips.appendChild(button);
  });
  tutorQuickRepliesEl.appendChild(chips);
}

function renderInteractionLog() {
  interactionLogEl.innerHTML = '';
  (uiState.interactionLog || []).forEach((entry) => {
    const li = document.createElement('li');
    li.textContent = `${entry.role}: ${entry.text}`;
    if (entry.role === 'usuario') {
      li.dataset.testid = 'chat-message-user';
    } else if (entry.role === 'livecopilot') {
      li.dataset.testid = 'chat-message-assistant';
    }
    interactionLogEl.appendChild(li);
  });
}

function pushInteraction(role, text, opts = {}) {
  const clean = String(text || '').trim();
  if (!clean) return;
  if (opts.dedup) {
    const normalized = normalizeTranscriptForUi(clean);
    if (normalized) {
      const dedupKey = String(opts.dedupKey || 'voice-transcript');
      const dedupToken = Number(opts.dedupToken || 0);
      const existing = uiState.interactionDedup[dedupKey] || { normalized: '', token: 0 };
      if (existing.normalized && existing.normalized === normalized && existing.token === dedupToken) {
        void emitVoiceEvent('transcript_render_suppressed', {
          transcript_duplicate_ignored: true,
          transcript_render_suppressed: true,
          transcript_render_reason: String(opts.dedupReason || 'normalized_match'),
          transcript_excerpt: summarizeForVoiceLog(clean, 180),
        });
        return;
      }
      uiState.interactionDedup[dedupKey] = { normalized, token: dedupToken };
    }
  }
  uiState.interactionLog.push({ role, text: clean });
  uiState.interactionLog = uiState.interactionLog.slice(-20);
  renderInteractionLog();
}

function clearSilenceGuardTranscript() {
  if (uiState.voice.pendingTranscriptGuardTimer) {
    clearTimeout(uiState.voice.pendingTranscriptGuardTimer);
  }
  uiState.voice.pendingTranscriptGuardTimer = null;
  uiState.voice.pendingTranscriptGuard = '';
}

function queueSilenceGuardTranscript(text, delayMs) {
  clearSilenceGuardTranscript();
  uiState.voice.pendingTranscriptGuard = text;
  const safeDelay = Math.max(Math.round(delayMs), MIN_SILENCE_GUARD_DELAY_MS);
  uiState.voice.pendingTranscriptGuardTimer = window.setTimeout(() => {
    const pending = uiState.voice.pendingTranscriptGuard;
    clearSilenceGuardTranscript();
    if (pending) {
      void emitVoiceEvent('voice_transcript_guard_released', {
        transcript_excerpt: summarizeForVoiceLog(pending, 180),
      });
      handleFinalTranscription(pending, { force: true });
    }
  }, safeDelay);
  void emitVoiceEvent('voice_transcript_guarded_for_silence', {
    transcript_excerpt: summarizeForVoiceLog(text, 180),
    guard_delay_ms: safeDelay,
  });
}

function calculateSilenceGuardDelay() {
  const lastStopped = Number(uiState.voice.timing.lastSpeechStoppedAtMs || 0);
  if (!lastStopped) return 0;
  const elapsed = nowPerfMs() - lastStopped;
  if (elapsed >= MIN_SILENCE_BEFORE_SUBMIT_MS) return 0;
  return MIN_SILENCE_BEFORE_SUBMIT_MS - elapsed;
}

function handleFinalTranscription(text, { force = false } = {}) {
  const clean = String(text || '').trim();
  if (!clean) return;
  if (!force) {
    const delay = calculateSilenceGuardDelay();
    if (delay > 0) {
      queueSilenceGuardTranscript(clean, delay);
      return;
    }
  }
  clearSilenceGuardTranscript();
  submitVoiceTranscriptToBackend(clean);
}

function renderVoiceMeta() {
  const diagnostics = uiState.voice.diagnostics || {};
  const rows = [
    `estado: ${uiState.voice.state}`,
    `sessao: ${uiState.voice.sessionId || 'nao iniciada'}`,
    `modelo: ${uiState.realtimeModel || 'indefinido'}`,
    `voz: ${uiState.realtimeVoice || 'indefinida'}`,
    `transporte: ${uiState.voice.transport}`,
    `ultimo_evento: ${uiState.voice.lastEvent || 'n/a'}`,
    `ultimo_evento_ts: ${uiState.voice.lastEventAt || 'n/a'}`,
    `backend_http: ${uiState.voice.lastBackendStatus || 'n/a'}`,
    `ultimo_erro: ${uiState.voice.lastError || 'nenhum'}`,
    `voice_output: ${uiState.voice.lastVoiceOutputStatus || 'n/a'}`,
    `trace_dir: ${uiState.voice.sessionTraceDir || 'n/a'}`,
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
  renderTutorQuickReplies(uiState.latestTutorOptions, uiState.latestContext);
  return Boolean(uiState.latestAnswer);
}

function shouldOverwriteAnswer(answer, knowledgeContext) {
  const cleanAnswer = String(answer || '').trim();
  if (!cleanAnswer) return false;
  const contextAccepted = Boolean(knowledgeContext?.context_candidate_accepted);
  if (contextAccepted) {
    return true;
  }
  const hasPreviousAnswer = Boolean(uiState.latestAnswer && uiState.latestAnswer.trim());
  if (!hasPreviousAnswer) {
    return true;
  }
  if (Boolean(knowledgeContext?.bad_transcript_ignored)) {
    return false;
  }
  return false;
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
    uiState.latestTutorOptions = Array.isArray(uiState.latestContext.tutor_next_options)
      ? uiState.latestContext.tutor_next_options
      : [];
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
    remoteAudioEl.removeAttribute('src');
    try { remoteAudioEl.pause(); } catch (_) {}
    try { remoteAudioEl.load(); } catch (_) {}
  }
  clearBackendAudioSource();
  uiState.voice.pc = null;
  uiState.voice.dc = null;
  uiState.voice.localStream = null;
  uiState.voice.assistantTranscript = '';
  uiState.voice.requestInFlight = false;
  uiState.voice.lastSubmittedTranscript = '';
  uiState.voice.lastGreetingNormalized = '';
  uiState.voice.greetingResponseLocked = false;
  uiState.voice.greetingEquivalentDuplicateSuppressed = false;
  uiState.voice.lastGreetingNormalizedAt = 0;
  uiState.voice.pendingTranscript = '';
  uiState.voice.lastVoiceOutputStatus = '';
  uiState.voice.autoStopLogged = false;
  uiState.voice.transcriptDedupToken = 1;
  uiState.interactionDedup['voice-transcript'] = { normalized: '', token: uiState.voice.transcriptDedupToken };
  resetVoiceTiming();
}

function revokeBackendAudioUrl() {
  if (!uiState.voice.backendAudioObjectUrl) {
    return;
  }
  try {
    URL.revokeObjectURL(uiState.voice.backendAudioObjectUrl);
  } catch (_) {}
  uiState.voice.backendAudioObjectUrl = '';
}

function clearBackendAudioSource() {
  if (!backendAudioEl) {
    revokeBackendAudioUrl();
    return;
  }
  backendAudioEl.srcObject = null;
  backendAudioEl.removeAttribute('src');
  backendAudioEl.muted = false;
  try { backendAudioEl.pause(); } catch (_) {}
  try { backendAudioEl.currentTime = 0; } catch (_) {}
  try { backendAudioEl.load(); } catch (_) {}
  revokeBackendAudioUrl();
}

function base64ToBlob(base64Value, mimeType) {
  const binary = atob(base64Value);
  const bytes = new Uint8Array(binary.length);
  for (let idx = 0; idx < binary.length; idx += 1) {
    bytes[idx] = binary.charCodeAt(idx);
  }
  return new Blob([bytes], { type: mimeType });
}

function writeAsciiToDataView(view, offset, text) {
  for (let idx = 0; idx < text.length; idx += 1) {
    view.setUint8(offset + idx, text.charCodeAt(idx));
  }
}

function buildSilentWavBlob(durationMs = 160) {
  const sampleRate = 8000;
  const sampleCount = Math.max(1, Math.floor((sampleRate * durationMs) / 1000));
  const byteLength = sampleCount * 2;
  const buffer = new ArrayBuffer(44 + byteLength);
  const view = new DataView(buffer);

  writeAsciiToDataView(view, 0, 'RIFF');
  view.setUint32(4, 36 + byteLength, true);
  writeAsciiToDataView(view, 8, 'WAVE');
  writeAsciiToDataView(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeAsciiToDataView(view, 36, 'data');
  view.setUint32(40, byteLength, true);

  return new Blob([buffer], { type: 'audio/wav' });
}

function normalizeGreetingVariant(text) {
  const cleaned = String(text || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
  return cleaned.replace(/[!?.]+$/, '').trim();
}

function normalizeTranscriptForUi(text) {
  const cleaned = String(text || '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
  return cleaned.replace(/[!?.]+$/, '').trim();
}

async function primeBackendAudioOutput() {
  if (!backendAudioEl || uiState.voice.backendAudioPrimed) {
    return;
  }

  const silentBlob = buildSilentWavBlob();
  const objectUrl = URL.createObjectURL(silentBlob);
  try {
    backendAudioEl.autoplay = true;
    backendAudioEl.playsInline = true;
    backendAudioEl.muted = true;
    backendAudioEl.src = objectUrl;
    await backendAudioEl.play();
    backendAudioEl.pause();
    uiState.voice.backendAudioPrimed = true;
    void emitVoiceEvent('voice_output_playback_primed', {
      response_summary: 'player de audio do backend preparado via gesto do usuario',
      voice_output_generated: false,
      voice_output_present: false,
      voice_output_mime_type: 'audio/wav',
      voice_output_audio_length: silentBlob.size,
    });
  } catch (err) {
    void emitVoiceEvent('voice_output_playback_prime_failed', {
      response_summary: 'falha ao preparar player de audio do backend',
      error_message: summarizeForVoiceLog(err?.message || 'prime do audio falhou', 180),
      voice_output_generated: false,
      voice_output_present: false,
      voice_output_mime_type: 'audio/wav',
      voice_output_audio_length: silentBlob.size,
      voice_output_play_failed: true,
    });
  } finally {
    try { backendAudioEl.pause(); } catch (_) {}
    try { backendAudioEl.currentTime = 0; } catch (_) {}
    backendAudioEl.muted = false;
    backendAudioEl.removeAttribute('src');
    try { backendAudioEl.load(); } catch (_) {}
    try { URL.revokeObjectURL(objectUrl); } catch (_) {}
  }
}

async function playBackendVoiceOutput(voiceOutput, transcriptText = '') {
  const payload = voiceOutput && typeof voiceOutput === 'object' ? voiceOutput : {};
  const mimeType = String(payload.mime_type || 'audio/mpeg').trim() || 'audio/mpeg';
  const audioBase64 = String(payload.audio_base64 || '').trim();
  const voiceStatus = String(payload.voice_status || '').trim() || 'unknown';
  const audioLength = Number(payload.audio_bytes || audioBase64.length || 0);
  const voiceOutputPresent = Boolean(payload.audio_output_available && audioBase64);
  const voiceOutputGenerated = Boolean(voiceStatus === 'ready' && payload.audio_output_available);
  uiState.voice.timing.voiceOutputReceivedAtMs = nowPerfMs();
  uiState.voice.lastVoiceOutputStatus = voiceStatus;
  renderVoiceMeta();
  void emitVoiceEvent('voice_output_received', {
    transcript_excerpt: summarizeForVoiceLog(transcriptText, 180),
    response_summary: summarizeForVoiceLog(JSON.stringify({
      voice_status: voiceStatus,
      provider: payload.voice_provider || '',
      audio_output_available: Boolean(payload.audio_output_available),
      audio_bytes: audioLength,
      mime_type: mimeType,
    }), 220),
    voice_output_generated: voiceOutputGenerated,
    voice_output_present: voiceOutputPresent,
    voice_output_mime_type: mimeType,
    voice_output_audio_length: audioLength,
    ...buildVoiceLatencyFields({
      latency_backend_voice_output_ms: payload?.timing?.voice_output_ms,
    }),
  });
  if (!voiceOutputPresent) {
    return;
  }
  if (!backendAudioEl) {
    void emitVoiceEvent('voice_output_play_failed', {
      transcript_excerpt: summarizeForVoiceLog(transcriptText, 180),
      error_message: 'elemento de audio do backend indisponivel',
      response_summary: voiceStatus,
      voice_output_generated: voiceOutputGenerated,
      voice_output_present: voiceOutputPresent,
      voice_output_mime_type: mimeType,
      voice_output_audio_length: audioLength,
      voice_output_play_attempted: false,
      voice_output_play_failed: true,
    });
    return;
  }

  try {
    const audioBlob = base64ToBlob(audioBase64, mimeType);
    const objectUrl = URL.createObjectURL(audioBlob);
    clearBackendAudioSource();
    uiState.voice.backendAudioObjectUrl = objectUrl;
    backendAudioEl.autoplay = true;
    backendAudioEl.preload = 'auto';
    backendAudioEl.playsInline = true;
    backendAudioEl.onended = () => {
      clearBackendAudioSource();
    };
    backendAudioEl.src = objectUrl;
    try { backendAudioEl.load(); } catch (_) {}
    uiState.voice.timing.playRequestedAtMs = nowPerfMs();
    void emitVoiceEvent('voice_output_play_requested', {
      transcript_excerpt: summarizeForVoiceLog(transcriptText, 180),
      response_summary: summarizeForVoiceLog(`${voiceStatus} -> play()`, 120),
      voice_output_generated: voiceOutputGenerated,
      voice_output_present: voiceOutputPresent,
      voice_output_mime_type: mimeType,
      voice_output_audio_length: audioBlob.size,
      voice_output_play_attempted: true,
      ...buildVoiceLatencyFields({
        latency_backend_voice_output_ms: payload?.timing?.voice_output_ms,
      }),
    });
    await backendAudioEl.play();
    uiState.voice.timing.playStartedAtMs = nowPerfMs();
    uiState.voice.lastVoiceOutputStatus = 'playing';
    renderVoiceMeta();
    void emitVoiceEvent('voice_output_play_started', {
      transcript_excerpt: summarizeForVoiceLog(transcriptText, 180),
      response_summary: summarizeForVoiceLog(`${voiceStatus} -> reproduzindo`, 120),
      voice_output_generated: voiceOutputGenerated,
      voice_output_present: voiceOutputPresent,
      voice_output_mime_type: mimeType,
      voice_output_audio_length: audioBlob.size,
      voice_output_play_attempted: true,
      voice_output_play_succeeded: true,
      ...buildVoiceLatencyFields({
        latency_backend_voice_output_ms: payload?.timing?.voice_output_ms,
      }),
    });
  } catch (err) {
    uiState.voice.lastVoiceOutputStatus = 'play_failed';
    renderVoiceMeta();
    void emitVoiceEvent('voice_output_play_failed', {
      transcript_excerpt: summarizeForVoiceLog(transcriptText, 180),
      error_message: summarizeForVoiceLog(err?.message || 'falha ao iniciar audio de saida', 180),
      response_summary: voiceStatus,
      voice_output_generated: voiceOutputGenerated,
      voice_output_present: voiceOutputPresent,
      voice_output_mime_type: mimeType,
      voice_output_audio_length: audioLength,
      voice_output_play_attempted: true,
      voice_output_play_failed: true,
      ...buildVoiceLatencyFields({
        latency_backend_voice_output_ms: payload?.timing?.voice_output_ms,
      }),
    });
    setChatFeedback(`Resposta em texto exibida. Audio nao iniciou automaticamente: ${err?.message || 'falha de autoplay'}`, true);
  }
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

function summarizeForVoiceLog(value, limit = 160) {
  const clean = String(value || '').trim().replace(/\s+/g, ' ');
  if (clean.length <= limit) return clean;
  return `${clean.slice(0, Math.max(0, limit - 3)).trim()}...`;
}

function nowPerfMs() {
  if (typeof window.performance === 'object' && typeof window.performance.now === 'function') {
    return window.performance.now();
  }
  return Date.now();
}

function resetVoiceTiming() {
  uiState.voice.timing = {
    turnStartedAtMs: 0,
    transcriptionCompletedAtMs: 0,
    backendRequestSentAtMs: 0,
    backendResponseReceivedAtMs: 0,
    voiceOutputReceivedAtMs: 0,
    playRequestedAtMs: 0,
    playStartedAtMs: 0,
    lastSpeechStoppedAtMs: 0,
  };
}

function buildVoiceLatencyFields(extra = {}) {
  const timing = uiState.voice.timing || {};
  const turnStartedAtMs = Number(timing.turnStartedAtMs || 0);
  const transcriptionCompletedAtMs = Number(timing.transcriptionCompletedAtMs || 0);
  const backendRequestSentAtMs = Number(timing.backendRequestSentAtMs || 0);
  const backendResponseReceivedAtMs = Number(timing.backendResponseReceivedAtMs || 0);
  const voiceOutputReceivedAtMs = Number(timing.voiceOutputReceivedAtMs || 0);
  const playRequestedAtMs = Number(timing.playRequestedAtMs || 0);
  const playStartedAtMs = Number(timing.playStartedAtMs || 0);
  const duration = (start, end) => (start > 0 && end > 0 && end >= start ? Math.round(end - start) : undefined);
  return {
    latency_capture_to_transcription_ms: duration(turnStartedAtMs, transcriptionCompletedAtMs),
    latency_transcription_to_backend_send_ms: duration(transcriptionCompletedAtMs, backendRequestSentAtMs),
    latency_backend_wait_ms: duration(backendRequestSentAtMs, backendResponseReceivedAtMs),
    latency_backend_response_to_voice_output_ms: duration(backendResponseReceivedAtMs, voiceOutputReceivedAtMs),
    latency_voice_output_to_play_requested_ms: duration(voiceOutputReceivedAtMs, playRequestedAtMs),
    latency_play_request_to_started_ms: duration(playRequestedAtMs, playStartedAtMs),
    latency_capture_to_play_started_ms: duration(turnStartedAtMs, playStartedAtMs),
    ...extra,
  };
}

function summarizeRealtimeEvent(event) {
  if (!event || typeof event !== 'object') return '';
  const summary = {};
  const scalarKeys = ['type', 'event_id', 'response_id', 'item_id', 'output_index', 'content_index', 'role', 'status'];
  scalarKeys.forEach((key) => {
    const value = event[key];
    if (value !== undefined && value !== null && value !== '') {
      summary[key] = value;
    }
  });
  const errorMessage = String(event?.error?.message || '').trim();
  if (errorMessage) {
    summary.error_message = errorMessage;
  }
  const text = extractEventText(event);
  if (text) {
    summary.text = summarizeForVoiceLog(text, 120);
  }
  if (Array.isArray(event?.response?.output) && event.response.output.length) {
    summary.response_output_types = event.response.output
      .slice(0, 3)
      .map((item) => String(item?.type || '').trim())
      .filter(Boolean);
  }
  if (event?.item?.content?.[0]?.type) {
    summary.item_content_type = String(event.item.content[0].type).trim();
  }
  return summarizeForVoiceLog(JSON.stringify(summary), 220);
}

function summarizeRtcError(err) {
  if (!err) return '';
  const name = String(err.name || '').trim();
  const message = String(err.message || '').trim();
  const error = String(err.error || '').trim();
  return summarizeForVoiceLog([name, message, error].filter(Boolean).join(': '), 180);
}

function getVoiceTrackState(track) {
  if (!track) return '';
  return summarizeForVoiceLog(JSON.stringify({
    kind: String(track.kind || '').trim(),
    enabled: Boolean(track.enabled),
    muted: Boolean(track.muted),
    readyState: String(track.readyState || '').trim(),
    label: String(track.label || '').trim(),
  }), 220);
}

function emitTrackState(eventName, track, extra = {}) {
  if (!track) return;
  void emitVoiceEvent(eventName, {
    response_summary: getVoiceTrackState(track),
    ...extra,
  });
}

function markAutoStop(reason, detail = '') {
  if (uiState.voice.autoStopLogged) return;
  uiState.voice.autoStopLogged = true;
  uiState.voice.stopReason = reason;
  uiState.voice.stopDetail = detail;
  uiState.voice.stopRequestedAt = new Date().toISOString();
  void emitVoiceEvent('voice_session_auto_stopped', {
    response_summary: summarizeForVoiceLog(detail || reason, 180),
    provider_event_type: reason,
  });
}

async function emitVoiceEvent(eventName, payload = {}) {
  const sessionId = payload.session_id || uiState.voice.sessionId || '';
  const conversationId = payload.conversation_id || uiState.voice.conversationId || sessionId || '';
  const eventPayload = {
    event: eventName,
    session_id: sessionId,
    conversation_id: conversationId,
    source: 'frontend',
    transport: uiState.voice.transport || 'webrtc',
    ts: new Date().toISOString(),
    ...payload,
  };
  uiState.voice.lastEvent = String(eventName || '').trim();
  uiState.voice.lastEventAt = eventPayload.ts;
  if (eventPayload.http_status) {
    uiState.voice.lastBackendStatus = String(eventPayload.http_status);
  }
  if (eventPayload.error_message) {
    uiState.voice.lastError = summarizeForVoiceLog(eventPayload.error_message, 120);
  }
  renderVoiceMeta();
  console.info('voice_event', eventPayload);
  try {
    const res = await fetch('/api/voice/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventPayload),
      keepalive: true,
    });
    const payloadResponse = await res.json();
    if (res.ok && payloadResponse && payloadResponse.session_dir) {
      uiState.voice.sessionTraceDir = String(payloadResponse.session_dir || '').trim();
      renderVoiceMeta();
    }
  } catch (_) {
    // Observabilidade nao deve quebrar a trilha de voz.
  }
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
  uiState.voice.lastError = summarizeForVoiceLog(message, 120);
  void emitVoiceEvent('voice_error', {
    error_message: message,
    response_summary: 'ambiente sem suporte para captura',
  });
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
  void emitVoiceEvent(type === 'error' ? 'realtime_error_event' : 'realtime_event_received', {
    provider_event_type: type,
    response_summary: summarizeRealtimeEvent(event),
  });

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
    resetVoiceTiming();
    uiState.voice.timing.turnStartedAtMs = nowPerfMs();
    uiState.voice.timing.lastSpeechStoppedAtMs = 0;
    clearSilenceGuardTranscript();
    setVoiceState('live', ['canal: voz', 'evento: fala_detectada', 'estado: ouvindo para consultar']);
    return;
  }

  if (type === 'input_audio_buffer.speech_stopped') {
    uiState.voice.timing.lastSpeechStoppedAtMs = nowPerfMs();
    uiState.latestStatus = ['canal: voz', 'evento: fala_finalizada', 'estado: aguardando transcricao/resposta'];
    renderInteractionStatus();
    return;
  }

  if (type === 'conversation.item.input_audio_transcription.completed') {
    const text = extractEventText(event);
    if (text) {
      uiState.voice.timing.transcriptionCompletedAtMs = nowPerfMs();
      pushInteraction('voz->consulta', text, {
        dedup: true,
        dedupKey: 'voice-transcript',
        dedupToken: uiState.voice.transcriptDedupToken,
        dedupReason: 'normalized_voice_transcript',
      });
      uiState.latestStatus = ['canal: voz', 'evento: transcricao_final', 'fluxo: enviando ao backend unificado'];
      renderInteractionStatus();
      void emitVoiceEvent('transcription_completed', {
        transcript_excerpt: summarizeForVoiceLog(text, 180),
        provider_event_type: type,
        ...buildVoiceLatencyFields(),
      });
      handleFinalTranscription(text);
    }
    return;
  }

  if (type === 'response.output_audio_transcript.delta' || type === 'response.audio_transcript.delta') {
    return;
  }

  if (type === 'response.output_audio_transcript.done' || type === 'response.audio_transcript.done') {
    return;
  }

  if (type === 'response.done') {
    return;
  }

  if (type === 'error') {
    const text = extractEventText(event) || String(event?.error?.message || 'erro realtime');
    uiState.voice.lastError = summarizeForVoiceLog(text, 120);
    markAutoStop('realtime_error', text);
    void emitVoiceEvent('voice_error', {
      error_message: text,
      provider_event_type: type,
    });
    setVoiceState('error', [`canal: voz`, `erro: ${text}`]);
  }
}

async function submitVoiceTranscriptToBackend(text) {
  const cleanText = String(text || '').trim();
  if (!cleanText) return;
  clearSilenceGuardTranscript();
  const normalizedGreetingTranscript = normalizeGreetingVariant(cleanText);
  if (uiState.voice.requestInFlight) {
    if (cleanText === uiState.voice.lastSubmittedTranscript) {
      void emitVoiceEvent('voice_error', {
        error_message: 'transcricao final duplicada ignorada',
        transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
      });
      return;
    }
    const replacedTranscript = String(uiState.voice.pendingTranscript || '').trim();
    uiState.voice.pendingTranscript = cleanText;
    void emitVoiceEvent(replacedTranscript && replacedTranscript !== cleanText ? 'voice_transcript_replaced_in_queue' : 'voice_transcript_queued', {
      transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
      response_summary: summarizeForVoiceLog(replacedTranscript || 'transcricao final aguardando conclusao do request atual', 180),
      voice_transcript_final_only: true,
    });
    return;
  }

  if (cleanText === uiState.voice.lastSubmittedTranscript) {
    void emitVoiceEvent('voice_error', {
      error_message: 'transcricao final duplicada ignorada',
      transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
    });
    return;
  }

  uiState.voice.requestInFlight = true;
  uiState.voice.lastSubmittedTranscript = cleanText;
  uiState.voice.lastVoiceOutputStatus = '';
  uiState.voice.timing.backendRequestSentAtMs = nowPerfMs();
  setChatFeedback('Transcricao final recebida. Consultando o backend unificado do Livecopilot...');
  uiState.latestStatus = ['canal: voz', 'evento: backend_request', 'fluxo: voz -> transcricao -> /realtime/respond'];
  renderInteractionStatus();
  void emitVoiceEvent('voice_transcript_sent_to_backend', {
    transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
    voice_transcript_final_only: true,
    ...buildVoiceLatencyFields(),
  });

      try {
        const res = await fetch('/realtime/respond', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: cleanText,
            mode: modeSelect.value || 'generic',
            conversation_id: uiState.voice.conversationId || uiState.voice.sessionId || undefined,
            voice_output_enabled: true,
            voice_transcript_final_only: true,
          }),
        });
    const payload = await res.json();
    uiState.voice.timing.backendResponseReceivedAtMs = nowPerfMs();
    uiState.voice.lastBackendStatus = String(res.status);
    if (!res.ok) {
      void emitVoiceEvent('voice_error', {
        transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
        http_status: res.status,
        error_message: payload.error || 'falha no /realtime/respond',
      });
      throw new Error(payload.error || 'falha no /realtime/respond');
    }

    uiState.voice.conversationId = payload.conversation_id || uiState.voice.conversationId || uiState.voice.sessionId;
    uiState.conversationId = payload.conversation_id || uiState.conversationId;
    const knowledgeContext = payload.knowledge_context || {};
    uiState.latestTutorOptions = Array.isArray(knowledgeContext.tutor_next_options)
      ? knowledgeContext.tutor_next_options
      : [];
    renderTutorQuickReplies(uiState.latestTutorOptions, knowledgeContext);
    const greetingAnswerUsed = Boolean(knowledgeContext.greeting_answer_path_used);
    const greetingNormalizedFresh =
      normalizedGreetingTranscript &&
      nowPerfMs() - (uiState.voice.lastGreetingNormalizedAt || 0) < 30000;
    const equivalentGreetingSuppressed =
      normalizedGreetingTranscript &&
      greetingNormalizedFresh &&
      uiState.voice.greetingResponseLocked &&
      normalizedGreetingTranscript === uiState.voice.lastGreetingNormalized &&
      !greetingAnswerUsed;
    void emitVoiceEvent('voice_backend_response_received', {
      transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
      http_status: res.status,
      response_summary: summarizeForVoiceLog(payload.answer || '', 180),
      greeting_normalized_match: greetingAnswerUsed,
      greeting_normalized_value: normalizedGreetingTranscript || undefined,
      greeting_equivalent_duplicate_suppressed: equivalentGreetingSuppressed,
      ...buildVoiceLatencyFields({
        latency_backend_total_ms: payload?.latency_breakdown?.request_total_ms,
        latency_backend_build_reply_ms: payload?.latency_breakdown?.build_livecopilot_reply_ms,
        latency_backend_connector_ms: payload?.latency_breakdown?.connector_ms,
        latency_backend_voice_output_ms: payload?.latency_breakdown?.voice_output_ms,
      }),
    });
    if (equivalentGreetingSuppressed) {
      void emitVoiceEvent('voice_transcript_equivalent_suppressed', {
        transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
        greeting_equivalent_duplicate_suppressed: true,
        greeting_normalized_value: normalizedGreetingTranscript,
      });
      return;
    }
    uiState.latestContext = knowledgeContext;
    if (greetingAnswerUsed) {
      uiState.voice.lastGreetingNormalized = normalizedGreetingTranscript;
      uiState.voice.greetingResponseLocked = true;
      uiState.voice.lastGreetingNormalizedAt = nowPerfMs();
    }
    uiState.latestStatus = [
      'canal: voz',
      'motor: backend_unificado',
      `backend: ${payload.backend || 'n/a'}`,
      `stage: ${payload.response_stage || 'final'}`,
      `readiness: ${payload.readiness || 'n/a'}`,
      `latencia_ms: ${payload.latency_ms ?? 'n/a'}`,
    ];
    uiState.voice.assistantTranscript = String(payload.answer || '').trim();
    const responseSummary = summarizeForVoiceLog(payload.answer || '', 180);
    const shouldOverwrite = shouldOverwriteAnswer(payload.answer, knowledgeContext);
    if (shouldOverwrite) {
      updateAnswer(payload.answer, payload.bullets);
      pushInteraction('livecopilot', payload.answer || '');
    } else {
      void emitVoiceEvent('ui_response_overwrite_blocked', {
        transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
        response_summary: responseSummary,
        context_reject_reason: String(knowledgeContext.context_reject_reason || '').trim(),
        ui_response_overwrite_blocked: true,
      });
    }
    uiState.voice.transcriptDedupToken = Number(uiState.voice.transcriptDedupToken || 0) + 1;
    uiState.interactionDedup['voice-transcript'] = { normalized: '', token: uiState.voice.transcriptDedupToken };
    renderInteractionStatus();
    renderBackendContext();
    if (uiState.knowledgeDebugEnabled && payload.snapshot && payload.snapshot.knowledge_debug && knowledgeDebugEl) {
      knowledgeDebugEl.textContent = JSON.stringify(payload.snapshot.knowledge_debug, null, 2);
    }
    await playBackendVoiceOutput(payload.voice_output, cleanText);
    void emitVoiceEvent('voice_backend_response_rendered', {
      transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
      http_status: res.status,
      response_summary: summarizeForVoiceLog(payload.answer || '', 180),
      ...buildVoiceLatencyFields({
        latency_backend_total_ms: payload?.latency_breakdown?.request_total_ms,
        latency_backend_build_reply_ms: payload?.latency_breakdown?.build_livecopilot_reply_ms,
        latency_backend_connector_ms: payload?.latency_breakdown?.connector_ms,
        latency_backend_voice_output_ms: payload?.latency_breakdown?.voice_output_ms,
      }),
    });
    if (uiState.voice.lastVoiceOutputStatus === 'play_failed') {
      // Mantem o feedback explicito de falha de autoplay/playback.
    } else if (uiState.voice.lastVoiceOutputStatus === 'playing') {
      setChatFeedback('Resposta em texto e audio recebida do backend unificado do Livecopilot.');
    } else {
      setChatFeedback('Resposta da voz recebida do backend unificado do Livecopilot.');
    }
  } catch (err) {
    uiState.voice.lastSubmittedTranscript = '';
    uiState.voice.lastError = summarizeForVoiceLog(err.message || 'falha inesperada', 120);
    void emitVoiceEvent('voice_error', {
      transcript_excerpt: summarizeForVoiceLog(cleanText, 180),
      error_message: err.message || 'falha inesperada',
      http_status: Number(uiState.voice.lastBackendStatus || 0) || undefined,
    });
    setChatFeedback(`Erro na convergencia da voz: ${err.message || 'falha inesperada'}`, true);
    uiState.latestStatus = ['canal: voz', 'motor: backend_unificado', 'erro: true'];
    renderInteractionStatus();
  } finally {
    uiState.voice.requestInFlight = false;
    const pendingTranscript = String(uiState.voice.pendingTranscript || '').trim();
    if (pendingTranscript && pendingTranscript !== cleanText) {
      uiState.voice.pendingTranscript = '';
      void emitVoiceEvent('voice_transcript_dequeued', {
        transcript_excerpt: summarizeForVoiceLog(pendingTranscript, 180),
        response_summary: 'transcricao pendente despachada apos conclusao do request anterior',
      });
      void submitVoiceTranscriptToBackend(pendingTranscript);
    }
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
    await primeBackendAudioOutput();
    void emitVoiceEvent('voice_session_open_requested', {
      response_summary: 'inicio da abertura da sessao realtime',
    });
    const sessionRes = await fetch('/api/realtime/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: modeSelect.value || 'generic' }),
    });
    const sessionPayload = await sessionRes.json();
    void emitVoiceEvent('voice_session_open_response_received', {
      http_status: sessionRes.status,
      response_summary: summarizeForVoiceLog(JSON.stringify({
        status: sessionPayload.status,
        channel: sessionPayload.channel,
        provider: sessionPayload.provider,
        model: sessionPayload.model,
        voice: sessionPayload.voice,
        has_client_secret: Boolean(sessionPayload.client_secret),
      }), 220),
    });
    if (!sessionRes.ok) {
      throw new Error(sessionPayload.error || 'falha ao criar sessao realtime');
    }

    const pc = new RTCPeerConnection();
    const dc = pc.createDataChannel('oai-events');
    uiState.voice.autoStopLogged = false;
    uiState.voice.stopReason = '';
    uiState.voice.stopDetail = '';
    uiState.voice.stopRequestedAt = '';
    void emitVoiceEvent('rtc_peer_connection_created', {
      response_summary: summarizeForVoiceLog(JSON.stringify({
        iceConnectionState: pc.iceConnectionState,
        connectionState: pc.connectionState,
        signalingState: pc.signalingState,
      }), 220),
    });
    void emitVoiceEvent('rtc_datachannel_created', {
      response_summary: summarizeForVoiceLog(JSON.stringify({
        label: dc.label,
        readyState: dc.readyState,
        ordered: dc.ordered,
      }), 220),
    });
    void emitVoiceEvent('microphone_access_requested', {
      response_summary: 'inicio do getUserMedia(audio)',
    });
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    void emitVoiceEvent('microphone_access_granted', {
      response_summary: summarizeForVoiceLog(JSON.stringify({
        tracks: stream.getTracks().length,
        active: Boolean(stream.active),
        id: stream.id || '',
      }), 220),
    });
    stream.getTracks().forEach((track) => pc.addTrack(track, stream));
    stream.getTracks().forEach((track) => {
      emitTrackState('microphone_track_state', track, {
        provider_event_type: 'track_added',
      });
      track.onmute = () => {
        emitTrackState('microphone_track_state', track, { provider_event_type: 'track_mute' });
      };
      track.onunmute = () => {
        emitTrackState('microphone_track_state', track, { provider_event_type: 'track_unmute' });
      };
      track.onended = () => {
        const detail = getVoiceTrackState(track);
        markAutoStop('microphone_track_ended', detail);
        emitTrackState('microphone_track_state', track, { provider_event_type: 'track_ended' });
      };
    });

    pc.ontrack = (event) => {
      void emitVoiceEvent('rtc_track_received', {
        response_summary: summarizeForVoiceLog(JSON.stringify({
          streams: Array.isArray(event.streams) ? event.streams.length : 0,
          track_kind: String(event.track?.kind || '').trim(),
          track_state: String(event.track?.readyState || '').trim(),
        }), 220),
        provider_event_type: 'pc.ontrack',
      });
      if (remoteAudioEl) {
        remoteAudioEl.srcObject = event.streams[0];
      }
    };
    pc.oniceconnectionstatechange = () => {
      const detail = `ice=${pc.iceConnectionState}`;
      void emitVoiceEvent('rtc_ice_connection_state_changed', {
        response_summary: detail,
        provider_event_type: 'pc.oniceconnectionstatechange',
      });
      if (['failed', 'closed', 'disconnected'].includes(pc.iceConnectionState)) {
        markAutoStop(`ice_${pc.iceConnectionState}`, detail);
      }
    };
    pc.onsignalingstatechange = () => {
      void emitVoiceEvent('rtc_signaling_state_changed', {
        response_summary: `signaling=${pc.signalingState}`,
        provider_event_type: 'pc.onsignalingstatechange',
      });
    };
    pc.onicecandidateerror = (event) => {
      const detail = summarizeForVoiceLog(JSON.stringify({
        errorCode: event?.errorCode,
        errorText: event?.errorText,
        url: event?.url,
      }), 220);
      markAutoStop('ice_candidate_error', detail);
      void emitVoiceEvent('rtc_peer_connection_error', {
        error_message: detail || 'ice candidate error',
        provider_event_type: 'pc.onicecandidateerror',
      });
    };
    pc.onconnectionstatechange = () => {
      const detail = `connection=${pc.connectionState}`;
      void emitVoiceEvent('rtc_connection_state_changed', {
        response_summary: detail,
        provider_event_type: 'pc.onconnectionstatechange',
      });
      if (pc.connectionState === 'connected') {
        setVoiceState('live', ['canal: voz', 'estado: conectado', 'fluxo: voz pronta para consulta']);
      } else if (['failed', 'disconnected', 'closed'].includes(pc.connectionState)) {
        markAutoStop(`connection_${pc.connectionState}`, detail);
        setVoiceState('idle', ['canal: voz', `estado: ${pc.connectionState}`]);
      }
    };
    dc.onopen = () => {
      void emitVoiceEvent('rtc_datachannel_opened', {
        response_summary: summarizeForVoiceLog(JSON.stringify({
          label: dc.label,
          readyState: dc.readyState,
        }), 220),
        provider_event_type: 'dc.onopen',
      });
    };
    dc.onclose = () => {
      const detail = summarizeForVoiceLog(JSON.stringify({
        label: dc.label,
        readyState: dc.readyState,
      }), 220);
      markAutoStop('datachannel_closed', detail);
      void emitVoiceEvent('rtc_datachannel_closed', {
        response_summary: detail,
        provider_event_type: 'dc.onclose',
      });
    };
    dc.onerror = (event) => {
      const detail = summarizeRtcError(event);
      markAutoStop('datachannel_error', detail);
      void emitVoiceEvent('rtc_datachannel_error', {
        error_message: detail || 'erro no data channel',
        provider_event_type: 'dc.onerror',
      });
    };
    dc.onmessage = (event) => {
      const rawMessage = String(event?.data || '');
      void emitVoiceEvent('rtc_message_received', {
        response_summary: summarizeForVoiceLog(rawMessage, 220),
        provider_event_type: 'dc.onmessage',
      });
      try {
        handleRealtimeEvent(JSON.parse(event.data));
      } catch (err) {
        void emitVoiceEvent('rtc_message_parse_failed', {
          error_message: summarizeForVoiceLog(err?.message || 'falha ao parsear mensagem do data channel', 180),
          response_summary: summarizeForVoiceLog(rawMessage, 220),
          provider_event_type: 'dc.onmessage',
        });
      }
    };

    const offer = await pc.createOffer();
    void emitVoiceEvent('rtc_offer_created', {
      response_summary: summarizeForVoiceLog(JSON.stringify({
        type: offer.type,
        sdp_length: String(offer.sdp || '').length,
      }), 220),
    });
    await pc.setLocalDescription(offer);
    void emitVoiceEvent('rtc_local_description_set', {
      response_summary: summarizeForVoiceLog(JSON.stringify({
        type: pc.localDescription?.type || '',
        sdp_length: String(pc.localDescription?.sdp || '').length,
      }), 220),
    });

    const sdpRes = await fetch(`${sessionPayload.webrtc_url}?model=${encodeURIComponent(sessionPayload.model)}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${sessionPayload.client_secret}`,
        'Content-Type': 'application/sdp',
      },
      body: offer.sdp,
    });
    const answerSdp = await sdpRes.text();
    void emitVoiceEvent('rtc_remote_description_received', {
      http_status: sdpRes.status,
      response_summary: summarizeForVoiceLog(JSON.stringify({
        ok: sdpRes.ok,
        sdp_length: String(answerSdp || '').length,
      }), 220),
    });
    if (!sdpRes.ok) {
      throw new Error(answerSdp || 'falha ao negociar WebRTC com a OpenAI');
    }
    await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });
    void emitVoiceEvent('rtc_remote_description_set', {
      response_summary: summarizeForVoiceLog(JSON.stringify({
        type: pc.remoteDescription?.type || '',
        sdp_length: String(pc.remoteDescription?.sdp || '').length,
      }), 220),
    });

    uiState.voice.pc = pc;
    uiState.voice.dc = dc;
    uiState.voice.localStream = stream;
    uiState.voice.sessionId = `rt-${String(sessionPayload.expires_at || Date.now())}`;
    uiState.voice.sessionStartedAt = new Date().toISOString();
    uiState.voice.conversationId = uiState.voice.sessionId;
    uiState.voice.lastBackendStatus = '';
    uiState.voice.lastError = '';
    uiState.realtimeModel = sessionPayload.model || uiState.realtimeModel;
    uiState.realtimeVoice = sessionPayload.voice || uiState.realtimeVoice;
    renderVoiceMeta();
    void emitVoiceEvent('voice_session_started', {
      started_at: uiState.voice.sessionStartedAt,
      url: window.location.href,
      model: uiState.realtimeModel || sessionPayload.model || '',
      voice: uiState.realtimeVoice || sessionPayload.voice || '',
      secure_context: Boolean(diagnostics.secureContext),
      media_devices: Boolean(diagnostics.mediaDevicesAvailable),
      get_user_media: Boolean(diagnostics.getUserMediaAvailable),
      user_agent: navigator.userAgent || '',
      response_summary: 'sessao realtime iniciada para captura/transcricao',
      provider_event_type: 'session.created',
    });
    setVoiceState('live', ['canal: voz', 'estado: fale agora', 'fluxo: falar em vez de digitar']);
  } catch (err) {
    resetVoiceTransport();
    const message = describeVoiceError(err);
    uiState.voice.lastError = summarizeForVoiceLog(message, 120);
    markAutoStop('session_start_failed', message);
    void emitVoiceEvent('microphone_access_failed', {
      error_message: message,
      provider_event_type: 'getUserMedia/session_start_failed',
    });
    void emitVoiceEvent('voice_error', {
      error_message: message,
      provider_event_type: 'session.start_failed',
    });
    setVoiceState('error', [`canal: voz`, `erro: ${message}`]);
    setChatFeedback(`Erro de voz: ${message}`, true);
  }
}

function stopVoiceSession(reason = 'manual', detail = '') {
  uiState.voice.autoStopLogged = true;
  uiState.voice.stopReason = reason;
  uiState.voice.stopDetail = detail;
  uiState.voice.stopRequestedAt = new Date().toISOString();
  void emitVoiceEvent('voice_stop_requested', {
    response_summary: summarizeForVoiceLog(detail || reason, 180),
    provider_event_type: reason,
  });
  void emitVoiceEvent('voice_session_stopped', {
    response_summary: summarizeForVoiceLog(detail || 'sessao realtime encerrada', 180),
    provider_event_type: reason,
  });
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
  stopVoiceSession('manual', 'encerramento manual solicitado pelo usuario');
});

bootstrapStatus();
