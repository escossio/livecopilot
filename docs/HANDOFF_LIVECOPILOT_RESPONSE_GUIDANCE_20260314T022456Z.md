# Handoff Livecopilot Response Guidance 20260314T022456Z

## Objetivo
Criar uma camada persistente, simples e versionavel para respostas ensinadas explicitamente pelo usuario, sem abrir aprendizado automatico e sem mexer no nucleo dos conectores operacionais.

## O que foi criado
- arquivo canonico:
  - `data/response_guidance.json`
- servico:
  - `app/services/response_guidance.py`

## Estrutura do arquivo canonico
- `version`
- `rules[]`
- campos por regra:
  - `id`
  - `scope`
  - `trigger_type`
  - `match_examples`
  - `preferred_response`
  - `policy_notes`
  - `active`
  - `priority`
  - `created_at`
  - `updated_at`

## Regras iniciais
- saudacoes:
  - `bom dia`
  - `boa tarde`
  - `boa noite`
  - `oi`
  - `ola`
- identidade:
  - `quem esta falando?`
  - `com quem eu falo?`
  - `quem e voce?`
- fallbacks:
  - `unmapped_target`
  - `no_confident_source`

## Integracao
- `_build_livecopilot_reply()` consulta `resolve_response_guidance(...)`
- quando encontra regra aplicavel:
  - prioriza a resposta ensinada
  - marca `backend=response_guidance`
  - registra `knowledge_context.search_backend=response_guidance`
  - aponta a origem para `data/response_guidance.json`
- quando nao encontra regra:
  - preserva o comportamento atual

## Evidencia
- `bom dia`
  - `backend=response_guidance`
  - resposta: saudacao ensinada
- `quem esta falando?`
  - `backend=response_guidance`
  - resposta: identidade ensinada
- `como esta o servidor llm?`
  - `backend=response_guidance`
  - resposta: fallback de alvo nao mapeado
- `isso ai`
  - `backend=response_guidance`
  - resposta: fallback de falta de fonte confiavel

## Testes
- `./.venv/bin/python -m py_compile app/services/response_guidance.py app/api/routes.py tests/test_response_guidance.py tests/test_livecopilot_interface_api.py`
- `./.venv/bin/python -m unittest -v tests/test_response_guidance.py tests/test_livecopilot_interface_api.py`
- `./.venv/bin/python -m unittest -v tests/test_infra_status_connector.py tests/test_response_guidance.py tests/test_livecopilot_interface_api.py`

## Publicacao
- `systemctl restart livecopilot-web8000.service`
- `GET /health` local: `200`
- `GET /health` publicado: `503` transitorio na subida, depois `200`
- smoke publicado:
  - `bom dia`
  - `como esta o servidor llm?`

## Limitacoes
- sem aprendizado automatico
- sem interface de edicao
- match ainda simples: texto normalizado exato ou chave semantica explicita

## Proximo passo
Criar um fluxo controlado para adicionar/editar regras ensinadas mantendo `response_guidance.json` como fonte canonica.
