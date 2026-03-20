# Handoff - Correcao do 500 na pergunta de status do backend

## Contexto
A pergunta "qual o status do backend do livecopilot?" gerava `HTTP 500` no `/api/chat`. O objetivo foi reproduzir, diagnosticar e corrigir sem abrir outras frentes.

## Reproducao
- API local:
  - `POST http://127.0.0.1:8099/api/chat` com `{"text":"qual o status do backend do livecopilot?"}`
  - resultado: `HTTP 500` com `Internal Server Error`

## Causa raiz
- Traceback no `journalctl`:
  - `PermissionError: [Errno 13] Permission denied: '/lab/projects/livecopilot/data/operational_memory.jsonl'`
- O runtime roda como `postgres`, mas `data/operational_memory.jsonl` estava `root:root` e `644`.
- A excecao ocorreu em `append_event()` quando o `infra_status_connector` tentou gravar a memoria operacional.

## Correcao aplicada
- Backup:
  - `/lab/projects/livecopilot/data/operational_memory.jsonl.bak.20260315T045443Z`
- Ajuste minimo:
  - `chown postgres:postgres /lab/projects/livecopilot/data/operational_memory.jsonl`

## Validacao
- API local apos correcao:
  - `POST /api/chat` com a mesma pergunta -> `HTTP 200`
  - resposta coerente via `infra_status_connector`
- UI/laboratorio visual:
  - comando: `runuser -u liveui -- env LIVEUI_SKILL_MESSAGE='qual o status do backend do livecopilot?' /srv/liveui/scripts/run-playwright-skill-smoke.sh`
  - evidencias:
    - `/srv/liveui/artifacts/chat-skill-initial-2026-03-15T045506918Z.png`
    - `/srv/liveui/artifacts/chat-skill-final-2026-03-15T045506918Z.png`
    - `/srv/liveui/artifacts/chat-skill-log-2026-03-15T045506918Z.json`
- Regressao basica:
  - `runuser -u liveui -- /srv/liveui/scripts/run-playwright-smoke.sh`
  - evidencias:
    - `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T045518306Z.png`
    - `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T045518306Z.png`
    - `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T045518306Z.json`

## Arquivos tocados
- `docs/HANDOFF_LIVECOPILOT_BACKEND_STATUS_500_FIX_20260315T045528Z.md`
- `STATUS.md`
- `/lab/projects/livecopilot/data/operational_memory.jsonl` (permissao/ownership)
- `/lab/projects/livecopilot/data/operational_memory.jsonl.bak.20260315T045443Z`
- `STATUS.md.bak.20260315T045528Z`

## Observacoes
- Nenhuma mudanca em MikroTik ou voz.
- Nenhuma alteracao de contrato da API; apenas correção de permissao no arquivo de memoria operacional.
