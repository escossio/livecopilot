# Handoff - Base local de smokes do Livecopilot

## Objetivo
Consolidar quais smokes locais sao a base estavel atual e revalidar execucao real.

## Base local estavel atual
- Smoke A: chat web principal (2 mensagens sequenciais no mesmo fluxo)
  - comando: `runuser -u liveui -- /srv/liveui/scripts/run-playwright-smoke.sh`
  - script: `/srv/liveui/automation/smoke-chat-e2e.js`
  - criterio de sucesso: resposta 200 do `/api/chat` e incremento de mensagens do assistente na UI
- Smoke B: skill local estavel (status do projeto)
  - comando: `runuser -u liveui -- /srv/liveui/scripts/run-playwright-skill-smoke.sh`
  - script: `/srv/liveui/automation/smoke-chat-skill-local.js`
  - criterio de sucesso: resposta renderizada na UI para pergunta local estavel

## Observacoes de consolidacao
- A variante de continuidade (2 mensagens) esta embutida no Smoke A.
- Nenhum script foi alterado nesta rodada; apenas consolidacao e registro.

## Validacao executada
- Smoke A passou:
  - `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T050416763Z.png`
  - `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T050416763Z.png`
  - `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T050416763Z.json`
- Smoke B passou:
  - `/srv/liveui/artifacts/chat-skill-initial-2026-03-15T050426500Z.png`
  - `/srv/liveui/artifacts/chat-skill-final-2026-03-15T050426500Z.png`
  - `/srv/liveui/artifacts/chat-skill-log-2026-03-15T050426500Z.json`

## Limitacoes
- Dependencia do laboratorio liveui ativo.
- Chromium instavel no host; Firefox/Playwright permanece como browser operacional.

## Arquivos lidos
- `/srv/liveui/scripts/run-playwright-smoke.sh`
- `/srv/liveui/scripts/run-playwright-skill-smoke.sh`
- `/srv/liveui/automation/smoke-chat-e2e.js`
- `/srv/liveui/automation/smoke-chat-skill-local.js`

## Backups
- `STATUS.md.bak.20260315T050435Z`
