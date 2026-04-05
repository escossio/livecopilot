(function () {
  const els = {
    projectName: document.getElementById('project-name'),
    missionSubtitle: document.getElementById('mission-subtitle'),
    statusBadge: document.getElementById('status-badge'),
    lastUpdated: document.getElementById('last-updated'),
    clock: document.getElementById('clock'),
    missionCurrent: document.getElementById('mission-current'),
    nowCurrent: document.getElementById('now-current'),
    nowNext: document.getElementById('now-next'),
    nowAvoid: document.getElementById('now-avoid'),
    roundFocus: document.getElementById('round-focus'),
    stageIndex: document.getElementById('stage-index')
  };

  function tickClock() {
    if (!els.clock) return;
    const now = new Date();
    els.clock.textContent = now.toLocaleTimeString('pt-BR', { hour12: false });
  }

  function normalizeStatusClass(status) {
    const value = String(status || '').trim().toLowerCase();
    if (value === 'concluida' || value === 'concluída') return 'completed';
    if (value === 'em andamento') return 'in-progress';
    if (value === 'parcial') return 'partial';
    if (value === 'nao iniciada' || value === 'não iniciada') return 'not-started';
    if (value === 'fora do escopo atual') return 'out-of-scope';
    return 'partial';
  }

  function renderStageIndex(stages, currentStageNumber) {
    if (!els.stageIndex) return;
    els.stageIndex.innerHTML = '';

    (stages || []).forEach((stage) => {
      const stageNum = Number(stage.number || 0);
      const isCurrent = stageNum === Number(currentStageNumber);
      const statusClass = normalizeStatusClass(stage.status);

      const row = document.createElement('article');
      row.className = `stage-row ${statusClass}${isCurrent ? ' current' : ''}`;

      const left = document.createElement('div');
      left.className = 'stage-main';

      const title = document.createElement('h3');
      title.className = 'stage-title';
      title.textContent = `${stageNum}. ${stage.name || 'Etapa sem nome'}`;
      left.appendChild(title);

      const desc = document.createElement('p');
      desc.className = 'stage-desc';
      desc.textContent = stage.description || '--';
      left.appendChild(desc);

      const deps = document.createElement('p');
      deps.className = 'stage-deps';
      const depList = Array.isArray(stage.dependencies) ? stage.dependencies : [];
      deps.textContent = depList.length ? `depende de: ${depList.join(', ')}` : 'depende de: -';
      left.appendChild(deps);

      const right = document.createElement('div');
      right.className = 'stage-side';

      const pill = document.createElement('span');
      pill.className = `status-pill ${statusClass}`;
      pill.textContent = stage.status || '--';
      right.appendChild(pill);

      if (isCurrent) {
        const flag = document.createElement('span');
        flag.className = 'current-flag';
        flag.textContent = 'ETAPA ATUAL';
        right.appendChild(flag);
      }

      row.appendChild(left);
      row.appendChild(right);
      els.stageIndex.appendChild(row);
    });
  }

  function renderState(state) {
    if (!state || typeof state !== 'object') return;

    if (els.projectName) els.projectName.textContent = state.project_name || 'Livecopilot';
    if (els.missionSubtitle) els.missionSubtitle.textContent = state.mission_subtitle || '--';
    if (els.lastUpdated) els.lastUpdated.textContent = state.last_updated || '--';
    if (els.missionCurrent) els.missionCurrent.textContent = state.mission_current || '--';
    if (els.roundFocus) els.roundFocus.textContent = state.round_focus || '--';

    if (els.statusBadge) {
      const badge = state.status_badge || {};
      const kind = String(badge.kind || 'partial').trim();
      els.statusBadge.className = `status-badge ${kind}`;
      els.statusBadge.textContent = badge.label || 'SEM STATUS';
    }

    const now = state.now || {};
    if (els.nowCurrent) els.nowCurrent.textContent = now.current_stage || '--';
    if (els.nowNext) els.nowNext.textContent = now.next_step || '--';
    if (els.nowAvoid) els.nowAvoid.textContent = now.avoid_now || '--';

    const currentStageNumber = now.current_stage_number || 0;
    renderStageIndex(state.stage_index || [], currentStageNumber);
  }

  async function loadState() {
    try {
      const resp = await fetch('/project-status-data', { cache: 'no-store' });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const payload = await resp.json();
      renderState(payload);
    } catch (err) {
      if (els.statusBadge) {
        els.statusBadge.className = 'status-badge not-started';
        els.statusBadge.textContent = 'ERRO DE LEITURA';
      }
      if (els.missionCurrent) {
        els.missionCurrent.textContent = 'Falha ao carregar docs/project_status_state.json.';
      }
    }
  }

  tickClock();
  setInterval(tickClock, 1000);
  loadState();
})();
