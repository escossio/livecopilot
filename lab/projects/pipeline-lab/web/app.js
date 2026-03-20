const API_BASE = `http://${window.location.hostname}:8000/api`;
const RUNS_ENDPOINT = `${API_BASE}/runs`;
const RUN_DETAIL = (id) => `${API_BASE}/runs/${id}`;
const RUN_NEXT_STAGE = (id) => `${API_BASE}/runs/${id}/next`;

const FALLBACK_RUNS = [
  {
    id: "fd999231-3b52-42a8-96f6-2dc761cc9a71",
    domain: "terraform",
    stage: "corpus_freeze",
    status: "completed",
    started_at: "2026-03-18T02:17:31.315175Z",
    metadata: {
      last_status: "completed",
      last_executed_stage: "source_manifest",
      executed_stages: [
        {
          stage: "source_policy",
          timestamp: "2026-03-18T02:27:14.469260Z",
          result: "executed stage source_policy at 2026-03-18T02:27:14.469260Z",
        },
        {
          stage: "source_manifest",
          timestamp: "2026-03-18T02:27:14.470451Z",
          result: "executed stage source_manifest at 2026-03-18T02:27:14.470451Z",
        },
      ],
    },
  },
];

const state = { runs: [], selectedRun: null };

const elements = {
  runList: document.getElementById("runList"),
  domainSelect: document.getElementById("domainSelect"),
  createRunBtn: document.getElementById("createRunBtn"),
  createMessage: document.getElementById("createMessage"),
  detailRunId: document.getElementById("detailRunId"),
  detailDomain: document.getElementById("detailDomain"),
  detailStage: document.getElementById("detailStage"),
  detailStatus: document.getElementById("detailStatus"),
  detailStart: document.getElementById("detailStart"),
  runHistory: document.getElementById("runHistory"),
  summaryText: document.getElementById("summaryText"),
  runLog: document.getElementById("runLog"),
  nextStageBtn: document.getElementById("nextStageBtn"),
  actionMessage: document.getElementById("actionMessage"),
  artifactList: document.getElementById("artifactList"),
};

document.addEventListener("DOMContentLoaded", () => {
  initCockpit();
  elements.nextStageBtn?.addEventListener("click", () => {
    if (!state.selectedRun) return;
    runNextStage(state.selectedRun);
  });
  elements.createRunBtn?.addEventListener("click", () => {
    const domain = elements.domainSelect?.value || "terraform";
    createRun(domain);
  });
});

async function initCockpit() {
  const runs = await loadRuns();
  state.runs = runs;
  renderRunList(runs);
  if (runs.length) {
    selectRun(runs[0].id);
  } else {
    elements.runList.innerHTML = "<p class=empty>nenhuma run registrada ainda.</p>";
  }
}

async function loadRuns() {
  try {
    const response = await fetch(RUNS_ENDPOINT);
    if (!response.ok) throw new Error("runs endpoint falhou");
    return await response.json();
  } catch (error) {
    console.warn("api runs inacessível, usando fallback", error);
    return FALLBACK_RUNS;
  }
}

async function loadRun(runId) {
  try {
    const response = await fetch(RUN_DETAIL(runId));
    if (!response.ok) throw new Error("detalhe da run falhou");
    const run = await response.json();
    return run;
  } catch (error) {
    console.warn("detalhe da run falhou", error);
    return (
      state.runs.find((run) => run.id === runId) || FALLBACK_RUNS[0]
    );
  }
}

function renderRunList(runs) {
  elements.runList.innerHTML = "";
  runs.forEach((run) => {
    const item = document.createElement("button");
    item.className = "run-item";
    item.dataset.runId = run.id;
    item.innerHTML = `
      <div>
        <strong>${run.domain}</strong>
        <span class="run-id">${run.id.slice(0, 8)}</span>
      </div>
      <p class="run-stage">${run.stage}</p>
    `;
    const badge = document.createElement("span");
    badge.className = `status-pill ${statusClass(run.status)}`;
    badge.textContent = run.status || "—";
    item.appendChild(badge);
    item.addEventListener("click", () => selectRun(run.id));
    elements.runList.appendChild(item);
  });
}

async function selectRun(runId) {
  state.selectedRun = runId;
  const run = await loadRun(runId);
  highlightSelected(runId);
  renderDetails(run);
  renderHistory(run);
  renderLog(run);
  renderArtifacts(run);
  updateActionMessage(run);
}

function highlightSelected(runId) {
  Array.from(elements.runList.children).forEach((child) => {
    child.classList.toggle("active", child.dataset.runId === runId);
  });
}

function renderDetails(run) {
  elements.detailRunId.textContent = run.id;
  elements.detailDomain.textContent = run.domain;
  elements.detailStage.textContent = run.stage;
  elements.detailStatus.textContent = run.status || "—";
  elements.detailStatus.className = `status-pill ${statusClass(run.status)}`;
  elements.detailStart.textContent = run.started_at || "—";
  elements.nextStageBtn.disabled = run.status === "running";
}

function renderHistory(run) {
  const history = run.metadata?.executed_stages || [];
  elements.runHistory.innerHTML = history.length
    ? history
        .map(
          (entry) =>
            `<li><strong>${entry.stage}</strong><span>${entry.timestamp}</span></li>`
        )
        .join("")
    : "<li>sem histórico disponível.</li>";
}

function renderLog(run) {
  const history = run.metadata?.executed_stages || [];
  if (!history.length) {
    elements.summaryText.textContent = "aguardando execução.";
    elements.runLog.textContent = "sem logs disponíveis.";
    return;
  }
  const summary = history[history.length - 1];
  const artifactSuffix = summary.artifact
    ? ` (artifact: ${summary.artifact})`
    : "";
  elements.summaryText.textContent = `${summary.result}${artifactSuffix}`;
  elements.runLog.textContent = history
    .map((entry) => `${entry.timestamp} - ${entry.stage}: ${entry.result}`)
    .join("\n");
}

function renderArtifacts(run) {
  if (!elements.artifactList) return;
  const history = run.metadata?.executed_stages || [];
  const artifacts = history.filter((entry) => entry.artifact);
  if (!artifacts.length) {
    elements.artifactList.innerHTML = "<li>nenhum artifact registrado.</li>";
    return;
  }
  elements.artifactList.innerHTML = artifacts
    .map(
      (entry) =>
        `<li><strong>${entry.stage}</strong><span>${entry.artifact}</span></li>`
    )
    .join("");
}

function statusClass(status) {
  if (!status) return "neutral";
  const normalized = status.toLowerCase();
  if (normalized.includes("blocked")) return "blocked";
  if (normalized.includes("completed")) return "success";
  return normalized.includes("running") ? "warning" : "neutral";
}

function updateActionMessage(run) {
  const blockedReason = run.metadata?.gate_blocked_reason || run.gate?.reason;
  elements.actionMessage.textContent = blockedReason
    ? `bloqueado: ${blockedReason}`
    : "clique em executar próximo stage para avançar";
}

async function runNextStage(runId) {
  elements.nextStageBtn.disabled = true;
  elements.nextStageBtn.textContent = "Executando...";
  elements.actionMessage.textContent = "efetuando gate...";
  try {
    const response = await fetch(RUN_NEXT_STAGE(runId), { method: "POST" });
    if (!response.ok) throw new Error("falha na execução");
    const payload = await response.json();
    elements.actionMessage.textContent = payload.result;
    await selectRun(runId);
  } catch (error) {
    elements.actionMessage.textContent = `erro: ${error.message}`;
  } finally {
    elements.nextStageBtn.textContent = "Executar próximo stage";
    elements.nextStageBtn.disabled = false;
  }
}

function setCreateMessage(message, variant) {
  if (!elements.createMessage) return;
  elements.createMessage.textContent = message;
  elements.createMessage.classList.remove("success", "error", "neutral");
  if (variant) {
    elements.createMessage.classList.add(variant);
  }
}

async function createRun(domain) {
  if (!elements.createRunBtn) return;
  elements.createRunBtn.disabled = true;
  elements.createRunBtn.textContent = "Criando...";
  setCreateMessage(`criando run para ${domain}...`, "neutral");
  try {
    const response = await fetch(RUNS_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain }),
    });
    if (!response.ok) throw new Error("não foi possível criar a run");
    const payload = await response.json();
    setCreateMessage(`run criada: ${payload.id}`, "success");
    const runs = await loadRuns();
    state.runs = runs;
    renderRunList(runs);
    await selectRun(payload.id);
  } catch (error) {
    setCreateMessage(`erro: ${error.message}`, "error");
  } finally {
    elements.createRunBtn.disabled = false;
    elements.createRunBtn.textContent = "Criar run";
  }
}
