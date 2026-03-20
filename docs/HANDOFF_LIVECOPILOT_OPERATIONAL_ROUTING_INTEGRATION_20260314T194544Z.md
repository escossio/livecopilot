# Livecopilot Operational Routing Integration

Timestamp: `2026-03-14T19:45:44Z`

## Objetivo da rodada

Integrar `operational_skills` ao pipeline principal do Livecopilot como camada oficial de roteamento de intencao, preservando o fallback atual e sem redesenhar a arquitetura existente.

## Ponto de integracao no pipeline

O ponto central de entrada continua em [`app/api/routes.py`](/lab/projects/livecopilot/app/api/routes.py).

Fluxo atual de decisao em `_build_livecopilot_reply(...)`:

1. normaliza `text_input` e resolve contexto da sessao
2. executa `_resolve_operational_skill_query(req, effective_input_text)` logo no inicio
3. se houver match de skill:
   - extrai `intent`, `target`, `source` e `action.operation`
   - chama o conector apropriado quando `source` aponta para conector integrado
   - registra evento em `operational_memory`
   - retorna resposta usando o payload do conector ou guidance estatico do catalogo
4. se nao houver match:
   - segue o fluxo existente com `process_ingest(...)`
   - tenta `resolve_infra_status_query(...)`
   - tenta `resolve_project_state_query(...)`
   - cai no restante do fluxo de sugestoes/semantic/fallback ja existente

## Integracao realizada

- `operational_skills` virou a primeira camada de roteamento do pipeline principal.
- Skills com `source=infra_status_connector` chamam `resolve_infra_status_query(...)`.
- Skills com `source=project_state_connector` chamam `resolve_project_state_query(...)`.
- Skills sem conector integrado ainda retornam resposta estatica guiada por `response_policy`.
- O fallback para o fluxo anterior permanece ativo quando nenhuma skill casa.
- O roteamento registra evento em `operational_memory`.
- O log passa a registrar:
  - `skill_id`
  - `intent`
  - `target`
  - `source`
  - `operation`

## Ajuste minimo de comportamento

Durante a validacao apareceu uma regressao: queries curtas roteadas por skill estavam sendo tratadas como resposta parcial e tinham a resposta do conector sobrescrita.

Correcao aplicada:

- a logica de `response_stage == "partial"` agora so rebaixa a resposta quando:
  - a entrada veio do buffer incremental de voz; ou
  - nenhum conector/skill retornou match

Impacto:

- queries textuais curtas como `status do postgres` e `status do servidor` agora preservam a resposta final do conector operacional
- o comportamento de prudencia para transcricao parcial continua ativo no fluxo de voz incremental

## Skills validadas manualmente

Queries executadas via `/api/chat`:

- `quantos dispositivos estao conectados na rede?`
  - skill: `mikrotik_connected_devices_count`
  - resultado: guidance estatico do catalogo
  - observacao: conector ainda nao integrado, comportamento esperado

- `status do postgres`
  - skill: `postgresql_health_check`
  - conector: `infra_status_connector`
  - resultado: resposta operacional real preservada

- `status do servidor`
  - skill: `server_local_health_check`
  - conector: `infra_status_connector`
  - resultado: resposta operacional real preservada

- `qual o ultimo checkpoint do projeto?`
  - skill: `project_latest_status`
  - conector: `project_state_connector`
  - resultado: resposta coerente com `STATUS.md` e handoff recente

## Testes executados

Validacao estatica:

```bash
./.venv/bin/python -m py_compile app/api/routes.py tests/test_livecopilot_interface_api.py
```

Suite executada:

```bash
./.venv/bin/python -m unittest -v \
  tests/test_livecopilot_interface_api.py \
  tests/test_operational_skills.py \
  tests/test_infra_status_connector.py \
  tests/test_response_guidance.py \
  tests/test_response_guidance_proposals.py
```

Resultado:

- `46 tests` executados
- `OK`

## Arquivos alterados

- [app/api/routes.py](/lab/projects/livecopilot/app/api/routes.py)
- [tests/test_livecopilot_interface_api.py](/lab/projects/livecopilot/tests/test_livecopilot_interface_api.py)

## Limitacoes restantes

- `mikrotik_connected_devices_count` continua apenas catalogado; nao ha conector integrado nesta rodada.
- A persistencia de sessao realtime ainda tem uma falha lateral em caminho `sessions.json.tmp -> sessions.json` quando o fluxo usa `conversation_id` em certas validacoes; isso nao foi alterado nesta rodada por nao fazer parte da integracao de roteamento.

## Conclusao

`operational_skills` agora esta plugado no fluxo principal como camada oficial de roteamento de intencao, com fallback preservado e sem quebra dos testes existentes. O pipeline passou a diferenciar melhor consultas operacionais curtas de transcricao parcial, o que era o principal risco funcional observado na integracao.
