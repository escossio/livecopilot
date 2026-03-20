# HANDOFF LIVECOPILOT LIVEUI CHAT E2E SMOKE 20260315T004702Z

## Status final

- Smoke E2E do chat web criado e executado com sucesso no laboratorio `liveui`
- Nenhuma mudanca no backend principal

## Seletor(es) reais usados

- input: `#chat-input`
- submit: `#chat-submit`
- form: `#chat-form`
- feedback: `#chat-feedback`

## Como o envio foi realizado

- preenchimento do textarea `#chat-input`
- clique no botao `#chat-submit`

## Criterio de resposta

- aguardou `POST /api/chat` com `200`
- extraiu `answer` do payload
- usou um snippet (primeiros 24 chars) para esperar renderizacao no DOM

## Evidencias geradas

- `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T034639496Z.png`
- `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T034639496Z.png`
- `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T034639496Z.json`

## Arquivos tocados

- `/srv/liveui/automation/smoke-chat-e2e.js`
- `/srv/liveui/scripts/run-playwright-smoke.sh`
- `/srv/liveui/automation/ui-inspect.js`
- `/srv/liveui/automation/ui-find-messages.js`
- `/lab/projects/livecopilot/STATUS.md`

## Comando para rodar o smoke

- `runuser -u liveui -- /srv/liveui/scripts/run-playwright-smoke.sh`

## Observacoes e limitacoes

- a UI nao expõe container de mensagens com id/class estavel; deteccao usa snippet do `answer`
- se a resposta do backend mudar drasticamente ou ficar vazia, o criterio falha por design
