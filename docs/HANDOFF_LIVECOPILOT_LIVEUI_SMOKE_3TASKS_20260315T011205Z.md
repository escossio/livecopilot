# HANDOFF LIVECOPILOT LIVEUI SMOKE 3 TASKS 20260315T011205Z

## Resumo

- Smoke E2E do chat endurecido com duas mensagens na mesma sessao.
- Criado smoke E2E de skill local estavel (status do projeto).
- Restart do laboratorio validado e smoke principal executado apos restart.

## Tarefa 1 - Smoke com duas mensagens

- Arquivo ajustado: `/srv/liveui/automation/smoke-chat-e2e.js`
- Mensagens:
  - "responda apenas OK"
  - "responda apenas TESTE2"
- Evidencias:
  - `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T040541633Z.png`
  - `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T040541633Z.png`
  - `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T040541633Z.json`

## Tarefa 2 - Smoke de skill local

- Pergunta escolhida: "qual o ultimo status do projeto?"
- Motivo: resposta previsivel via `project_state_connector`
- Tentativa anterior falhou com `500` ao perguntar status do backend.
- Arquivos criados:
  - `/srv/liveui/automation/smoke-chat-skill-local.js`
  - `/srv/liveui/scripts/run-playwright-skill-smoke.sh`
- Evidencias:
  - `/srv/liveui/artifacts/chat-skill-initial-2026-03-15T041033083Z.png`
  - `/srv/liveui/artifacts/chat-skill-final-2026-03-15T041033083Z.png`
  - `/srv/liveui/artifacts/chat-skill-log-2026-03-15T041033083Z.json`

## Tarefa 3 - Consolidacao operacional

- `systemctl stop liveui-lab.target` nao encerrou as units dependentes.
- Parada completa exigiu stop explicito das units.
- `systemctl start liveui-lab.target` reativou todas as units.
- noVNC respondeu `HTTP 200` apos restart.
- Smoke principal passou apos restart:
  - `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T041142407Z.png`
  - `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T041142407Z.png`
  - `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T041142407Z.json`
- Reboot nao executado por risco operacional ao host do backend.

## Comandos operacionais

- Smoke principal: `runuser -u liveui -- /srv/liveui/scripts/run-playwright-smoke.sh`
- Smoke skill local: `runuser -u liveui -- /srv/liveui/scripts/run-playwright-skill-smoke.sh`
- Start/stop/restart lab:
  - `systemctl start liveui-lab.target`
  - `systemctl stop liveui-lab.target`
  - `systemctl restart liveui-lab.target`

## Arquivos tocados

- `/srv/liveui/automation/smoke-chat-e2e.js`
- `/srv/liveui/automation/smoke-chat-skill-local.js`
- `/srv/liveui/scripts/run-playwright-skill-smoke.sh`
- `/lab/projects/livecopilot/STATUS.md`
