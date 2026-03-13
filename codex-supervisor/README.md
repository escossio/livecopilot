# codex-supervisor

Supervisor local para orquestrar um projeto-alvo externo usando o fluxo oficial do OpenAI Agents SDK com Codex CLI como MCP server (`MCPServerStdio`).

## Propósito

- Orquestrar execução de agente supervisor sem misturar arquivos com o projeto-alvo.
- Manter estado e logs somente neste repositório.
- Executar uma rodada real de validação conservadora antes de ações de edição.

## Arquitetura

- `supervisor/main.py`: CLI local.
- `supervisor/service.py`: facade estavel para integracoes externas (ex.: GPT proprio).
- `supervisor/http_api.py`: API HTTP minima para leitura de estado e disparo de execucao.
- `supervisor/api_client.py`: cliente Python minimo (urllib) para consumir a API local.
- `supervisor/gpt_adapter.py`: adaptador fino de decisao/orquestracao para runtime de GPT.
- `supervisor/gpt_tool_host.py`: wrapper executavel local (JSON stdout) para plugar em GPT real.
- `supervisor/project_journal.py`: persistencia de checkpoints e STATUS.md no projeto-alvo.
- `supervisor/workflow.py`: fluxo real `Agent + Runner.run(...)`.
- `supervisor/config.py`: resolve `agent_session_id` estavel e `SESSION_DB_PATH`.
- `supervisor/codex_bridge.py`: sobe/desce `MCPServerStdio` com `npx -y codex mcp-server`.
- `state/`: estado persistido do supervisor.
- `logs/`: logs locais do orquestrador.
- projeto-alvo: workspace externo apontado por `TARGET_PROJECT_PATH`.

## Fluxo de execução

1. Carrega `.env` e configuração do supervisor.
2. Valida `OPENAI_API_KEY` e `TARGET_PROJECT_PATH`.
3. Sobe Codex CLI como MCP server via `MCPServerStdio`.
4. Cria `Agent(..., mcp_servers=[codex_mcp_server])`.
5. Cria/reusa `SQLiteSession(session_id, db_path)`.
6. Executa rodada com `Runner.run(..., session=session)` e `max_turns` pequeno.
7. Inspeciona `result.new_items` para capturar `codex_thread_id` do tool result do Codex MCP.
8. Se o caminho alto nivel nao expuser o ID, usa fallback de observabilidade no `message_handler` do MCP server.
9. Persiste saída real em `state/last_action.json` e resumo em `state/next_step.md`.
10. Por padrao, grava checkpoint textual no projeto-alvo (`.supervisor/checkpoints/`) e atualiza/cria `STATUS.md`.

## Sessao persistente real (Agents SDK)

- O supervisor agora usa `SQLiteSession` para continuidade real entre rodadas.
- O `agent_session_id` e estavel:
  - prioridade 1: `--session-id`
  - prioridade 2: `AGENT_SESSION_ID` no ambiente
  - prioridade 3: derivacao estavel de `TARGET_PROJECT_PATH` (slug + hash curto)
- O backend e persistido em SQLite (`SESSION_DB_PATH`, padrao: `state/agent_sessions.db`).
- Cada rodada salva metadados em `state/last_action.json` e checkpoint JSON em `state/checkpoints/`.

Importante:
- `agent_session_id` (Agents SDK) **nao** e `codex_thread_id` (tool do Codex).
- O supervisor tenta capturar `codex_thread_id` do resultado do tool em `result.new_items`.
- Fonte primaria: `structuredContent.threadId`.
- Fallbacks, em ordem: `structuredContent.thread_id`, `threadId`, `thread_id`, `conversationId`, `conversation_id`.
- `conversationId` e apenas compatibilidade legada, nunca preferencia.
- Se nao houver campo exposto no payload do SDK/tool, o supervisor tenta fallback de baixo nivel no wrapper MCP.
- Fallback oficial do projeto: `bridge.observed_thread_id` (capturado pelo `message_handler` e/ou por warning `codex/event` quando necessario).
- Status persistido de origem:
  - `captured_from_mcp_tool_result` (prioridade alta)
  - `captured_from_mcp_message_handler` (fallback)
  - `pending_capture_from_mcp_tool_result` (nao capturado)

## Setup

```bash
cd /lab/projects/codex-supervisor
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade openai openai-agents python-dotenv
cp .env.example .env
```

Edite `.env`:

```env
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
TARGET_PROJECT_PATH=/lab/projects/target-project
SUPERVISOR_DEFAULT_TARGET_PROJECT_PATH=/lab/projects/livecopilot
SUPERVISOR_HOME=/lab/projects/codex-supervisor
SUPERVISOR_LOG_LEVEL=INFO
SESSION_DB_PATH=/lab/projects/codex-supervisor/state/agent_sessions.db
AGENT_SESSION_ID=
SUPERVISOR_MCP_AUDIT=0
SUPERVISOR_MCP_WARNING_CAPTURE=1
SUPERVISOR_PROJECT_JOURNAL=1
SUPERVISOR_CONTINUE_STRICT=0
SUPERVISOR_DEPLOY_PROFILE=compat
SUPERVISOR_CONTINUE_EXPECTED_MIN_VERSION=
SUPERVISOR_RUN_MAX_TURNS=2
SUPERVISOR_JOB_TIMEOUT_SECONDS=180
```

`SUPERVISOR_PROJECT_JOURNAL`:
- `1` (padrao): tenta gravar checkpoint no projeto-alvo e atualizar/criar `STATUS.md` a cada rodada (`run-once` e `continue-run`).
- `0`: desabilita essa escrita no projeto-alvo, mantendo apenas `state/` e `logs/` do supervisor.

## Execução

### Rodada nova (`--run-once`)

```bash
cd /lab/projects/codex-supervisor
source .venv/bin/activate
python3 -m supervisor.main --target-project /lab/projects/<repo_alvo> --run-once

# opcional: fixar manualmente o id da sessao do agente
python3 -m supervisor.main \
  --target-project /lab/projects/<repo_alvo> \
  --session-id agent-meu-projeto \
  --run-once
```

### Continuação explícita (`--continue-run`)

```bash
cd /lab/projects/codex-supervisor
source .venv/bin/activate
python3 -m supervisor.main --continue-run
```

## Integração com GPT próprio

O `codex-supervisor` pode atuar como backend operacional.
Seu GPT proprio fica na camada de decisao e chama apenas as operacoes estaveis abaixo.
O contrato principal continua sendo a API HTTP; o cliente Python e apenas conveniencia.
Camadas:
- `SupervisorApiClient` = transporte/acesso aos endpoints.
- `SupervisorGptAdapter` = decisao e orquestracao (`run_once` vs `continue_run`).

### Contrato de interface

Operacoes disponiveis:
- Ler status/resumo: `GET /status`
- Ler ultimo estado: `GET /last-action`
- Ler proximo passo: `GET /next-step`
- Disparar rodada nova: `POST /run-once`
- Disparar retomada: `POST /continue-run`
- Ler cauda de auditoria (opcional): `GET /audit-tail?limit=20`

Campos minimos recomendados para decisao do GPT (via `GET /status`):
- `target_project_path`
- `last_status`
- `codex_thread_id`
- `codex_continue_mode`
- `codex_continue_status`
- `deploy_profile`
- `can_continue`

### Subir API HTTP minima

```bash
cd /lab/projects/codex-supervisor
source .venv/bin/activate
python3 -m supervisor.http_api --host 127.0.0.1 --port 8787 --init-state
```

Com token opcional:

```bash
cd /lab/projects/codex-supervisor
source .venv/bin/activate
SUPERVISOR_API_TOKEN=<TOKEN_FOR_GPT> python3 -m supervisor.http_api --host 127.0.0.1 --port 8787
```

Quando `SUPERVISOR_API_TOKEN` estiver definido, envie `Authorization: Bearer <TOKEN_FOR_GPT>`.

Exemplos:

```bash
curl -s http://127.0.0.1:8787/status
curl -s http://127.0.0.1:8787/last-action
curl -s http://127.0.0.1:8787/next-step
curl -s "http://127.0.0.1:8787/audit-tail?limit=10"
curl -s -X POST http://127.0.0.1:8787/run-once \
  -H "Content-Type: application/json" \
  -d '{"target_project_path":"/lab/projects/<repo_alvo>","session_id":"agent-meu-projeto"}'
curl -s -X POST http://127.0.0.1:8787/continue-run

# smoke de resposta HTTP (sempre 202 + JSON com job_id)
curl -i -X POST http://127.0.0.1:8787/continue-run
# HTTP/1.0 202 Accepted
# Content-Type: application/json; charset=utf-8
# Connection: close
# {"accepted":true,"job_id":"<uuid>","status":"queued"}

# polling do job enfileirado
curl -s http://127.0.0.1:8787/jobs/<job_id>
curl -s http://127.0.0.1:8787/jobs/<job_id>/result
```

### Segurança minima da interface

- Sem execucao arbitraria de comandos.
- Apenas rotas de leitura de estado e disparo dos fluxos oficiais.
- Sem retorno de segredos por design.
- Recomendado bind local (`127.0.0.1`) e token para integracoes externas.
- `GET /audit-tail` retorna apenas resumo curto das entradas (sem blob completo).
- Fallback local de contexto (`README.md`) e somente leitura, restrito a `target_project_path`, bloqueando escape de path e limitado a `200KB`.

Regras:
- `--run-once` e `--continue-run` sao mutuamente exclusivos.
- `--continue-run` carrega e valida `state/last_action.json`.
- Se `--target-project` for informado em `--continue-run`, precisa bater com o `target_project_path` persistido.
- Se `--session-id` for informado em `--continue-run`, precisa bater com o `agent_session_id` persistido.
- A API nao enfileira multiplos jobs simultaneos: se houver job `queued/running`, um novo `POST` retorna erro `400` para evitar fila lenta.
- `SUPERVISOR_JOB_TIMEOUT_SECONDS` limita o tempo total de cada job; quando estoura, o job fecha como `failed` com erro `timeout`.

Regra operacional para GPT/HTTP:
- Nunca chame `POST /run-once` sem `target_project_path` explicito no payload.
- Mesmo com fallback por `SUPERVISOR_DEFAULT_TARGET_PROJECT_PATH`, o recomendado e sempre explicitar o alvo.
- Caminho padrao recomendado para esse ambiente: `/lab/projects/livecopilot`.
- `target_project_path=/lab/projects` (e `/lab`) e bloqueado por seguranca e retorna erro `400`.

Pre-requisitos minimos para `--continue-run`:
- `agent_session_id` valido
- `codex_thread_id` valido
- `codex_thread_id_status` valido
- `target_project_path` valido

Comportamento do `--continue-run`:
1. Faz discovery de capability/tool de continue via `list_tools`.
2. Se `codex-reply` estiver disponivel, ele e tratado como contrato oficial congelado e rota primaria deterministica para enviar `codex_thread_id`.
3. Se houver ack explicito, segue a rodada mantendo `SQLiteSession` e contexto persistido.
4. Se a rota primaria falhar ou nao houver discovery valido, cai para heuristica de compatibilidade (multi-rota).
5. Se nenhuma rota explicita for confirmada, faz fallback seguro para continuidade textual + mesma `SQLiteSession`.

Modo estrito de producao:
- `SUPERVISOR_CONTINUE_STRICT=1` bloqueia fallback heuristico/textual quando `codex-reply` falha ou nao existe.
- Nesse modo, a rodada encerra com erro explicito e auditoria `codex_continue_strict_mode_blocked_fallback`.

Profiles de deploy:
- `SUPERVISOR_DEPLOY_PROFILE=compat`:
  - valida o contrato congelado (`codex-reply`) quando possivel
  - permite fallback heuristico e, se necessario, context fallback
- `SUPERVISOR_DEPLOY_PROFILE=production`:
  - exige contrato valido de `codex-reply` (tool presente + schema com `threadId` e `prompt`)
  - opcionalmente aplica piso de versao com `SUPERVISOR_CONTINUE_EXPECTED_MIN_VERSION`
  - bloqueia heuristica/context fallback quando validacao falha
  - ativa comportamento estrito efetivo mesmo se `SUPERVISOR_CONTINUE_STRICT=0`

Regra pratica para GPT proprio:
1. Ler `GET /status`.
2. Se `can_continue=true` e `codex_thread_id` presente, preferir `POST /continue-run`.
3. Se `can_continue=false` ou sem thread, usar `POST /run-once`.
4. Sempre reconsultar `GET /status` apos cada execucao.

### Cliente Python de conveniencia

Importe o cliente:

```python
from supervisor.api_client import SupervisorApiClient

client = SupervisorApiClient(
    base_url="http://127.0.0.1:8787",
    token=None,  # ou token bearer
    timeout=30.0,
)
```

Metodos disponiveis:
- `get_status()`
- `get_last_action()`
- `get_next_step()`
- `get_audit_tail(limit=10)`
- `run_once(target_project_path=None, session_id=None)`
- `continue_run()`

Fluxo recomendado para GPT proprio:
1. `status = client.get_status()`
2. Se `status["can_continue"]` e `status["codex_thread_id"]`, usar `client.continue_run()`
3. Caso contrario, usar `client.run_once()`
4. Depois ler `client.get_last_action()` e `client.get_next_step()`

Exemplo curto:

```python
from supervisor.api_client import SupervisorApiClient

client = SupervisorApiClient()
status = client.get_status()
if status.get("can_continue") and status.get("codex_thread_id"):
    result = client.continue_run()
else:
    result = client.run_once()
print(result["status"])
print(client.get_next_step())
```

Demo opcional via modulo:

```bash
python3 -m supervisor.api_client --status
python3 -m supervisor.api_client --audit-tail --limit 10
python3 -m supervisor.api_client --run-once --target-project-path /lab/projects/<repo_alvo>
python3 -m supervisor.api_client --continue-run
```

### Adaptador fino para GPT

`SupervisorGptAdapter` encapsula o fluxo padrao:
1. ler `status`
2. decidir `continue_run` quando `can_continue=true` e `codex_thread_id` presente
3. executar a acao
4. retornar payload estruturado com resultado + estado

Retorno de `decide_and_execute(...)`:
- `decision`
- `execution_result`
- `last_action`
- `next_step`
- `status_snapshot`
- `ok` + `error` (quando falha)

Exemplo minimo:

```python
from supervisor.api_client import SupervisorApiClient
from supervisor.gpt_adapter import SupervisorGptAdapter

client = SupervisorApiClient(base_url="http://127.0.0.1:8787", token=None, timeout=30.0)
adapter = SupervisorGptAdapter(client=client)

result = adapter.decide_and_execute()
if result["ok"]:
    print(result["decision"])
    print(result["next_step"])
else:
    print(result["error"]["kind"], result["error"]["message"])
```

Forcando modo (opcional):

```python
result = adapter.decide_and_execute(force_mode="run_once")
# ou
result = adapter.decide_and_execute(force_mode="continue_run")
```

Demo opcional via modulo:

```bash
python3 -m supervisor.gpt_adapter
python3 -m supervisor.gpt_adapter --force-mode continue_run
python3 -m supervisor.gpt_adapter --force-mode run_once --target-project-path /lab/projects/<repo_alvo>
```

### Wrapper executavel para GPT real

`supervisor.gpt_tool_host` e o ponto mais simples para integrar com runtime externo (tool local/script host).
Ele:
- recebe parametros simples
- chama `SupervisorGptAdapter.decide_and_execute(...)`
- imprime JSON puro no `stdout` (sem logs ruidosos)

Contrato formal desta tool:
- [docs/gpt_tool_host_contract.md](/lab/projects/codex-supervisor/docs/gpt_tool_host_contract.md)

Launcher recomendado (facilita uso repetido):

```bash
./scripts/run_gpt_tool_host.sh
./scripts/run_gpt_tool_host.sh --force-mode continue_run
./scripts/run_gpt_tool_host.sh --target-project-path /lab/projects/<repo_alvo>
```

Ele faz apenas:
- entra na raiz do projeto
- ativa `.venv` se existir
- repassa os argumentos para `python3 -m supervisor.gpt_tool_host`

Comandos diretos (sem launcher), quando necessario:

```bash
python3 -m supervisor.gpt_tool_host
python3 -m supervisor.gpt_tool_host --force-mode continue_run
python3 -m supervisor.gpt_tool_host --target-project-path /lab/projects/<repo_alvo>
python3 -m supervisor.gpt_tool_host --base-url http://127.0.0.1:8787 --timeout 30
```

### Registro operacional em runtime local de GPT

Forma recomendada (mais segura): token via ambiente.
Evita expor segredo em linha de comando, historico de shell e logs de runtime.

```bash
export SUPERVISOR_API_TOKEN=<TOKEN_FOR_GPT>
./scripts/run_gpt_tool_host.sh \
  --base-url http://127.0.0.1:8787 \
  --timeout 30
```

Exemplo generico de registro quando o runtime aceita `command` + `args`:

```json
{
  "name": "codex-supervisor-gpt-tool-host",
  "command": "/lab/projects/codex-supervisor/scripts/run_gpt_tool_host.sh",
  "args": [
    "--base-url", "http://127.0.0.1:8787",
    "--timeout", "30"
  ],
  "env": {
    "SUPERVISOR_API_TOKEN": "<TOKEN_FOR_GPT>"
  }
}
```

Compatibilidade (uso excepcional): token explicito por argumento.

```bash
./scripts/run_gpt_tool_host.sh \
  --base-url http://127.0.0.1:8787 \
  --token <TOKEN_FOR_GPT> \
  --timeout 30
```

Prioridade de credencial no wrapper:
1. `--token` (se informado)
2. `SUPERVISOR_API_TOKEN` (ambiente)
3. sem token (`None`)

Exemplo de integracao via subprocess (runtime local):

```python
import json
import subprocess

proc = subprocess.run(
    ["/lab/projects/codex-supervisor/scripts/run_gpt_tool_host.sh", "--force-mode", "continue_run"],
    capture_output=True,
    text=True,
    check=False,
)
payload = json.loads(proc.stdout)
if payload["ok"]:
    print(payload["decision"], payload["next_step"])
else:
    print(payload["error"]["kind"], payload["error"]["message"])
```

Opcional (subprocess direto no modulo Python):

```python
proc = subprocess.run(
    ["python3", "-m", "supervisor.gpt_tool_host", "--force-mode", "continue_run"],
    capture_output=True,
    text=True,
    check=False,
)
```

## Limitação atual (pendência conhecida)

- A continuidade da sessao do supervisor ja e real via `SQLiteSession`.
- A captura de `codex_thread_id` depende do payload realmente exposto em `result.new_items` pelo SDK/tool.
- Se `structuredContent.threadId` vier no resultado, o valor e persistido com status de captura.
- Se nao vier, o fallback do wrapper MCP pode fornecer `codex_thread_id` por hint observado.
- Se nenhuma fonte real trouxer o ID, o estado permanece pendente sem falsificacao do identificador.
- A continuacao explicita por `codex_thread_id` agora prioriza rota deterministica descoberta em runtime; quando discovery/execucao falha, o fluxo cai para heuristica e depois para fallback textual de forma auditada.
- Neste ambiente, `codex-reply` foi validado empiricamente como contrato oficial de continue e agora e priorizado como padrao.

## Journal no projeto-alvo

Quando `SUPERVISOR_PROJECT_JOURNAL=1`, ao final de cada rodada o supervisor tenta registrar no `TARGET_PROJECT_PATH`:
- `.supervisor/checkpoints/<timestamp>_<mode>.md`
- `STATUS.md` (atualiza no topo se existir; cria template minimo se nao existir)

Conteudo minimo gravado:
- timestamp UTC, mode (`run-once`/`continue-run`), deploy_profile, decision e status
- `agent_session_id` e `codex_thread_id` (quando houver)
- resumo curto de `final_output` (maximo 10 linhas, truncado)
- `next_step`
- links locais para `state/last_action.json` e checkpoint interno do supervisor

Falha de escrita no projeto-alvo:
- nao interrompe a rodada
- tenta registrar evento `project_journal_write_failed` na auditoria MCP (quando habilitada)
- persiste no estado final os campos `project_journal_written=false` e `project_journal_error`

## Observabilidade opcional (MCP/tool result)

- `SUPERVISOR_MCP_AUDIT=1` habilita auditoria compacta em `logs/codex_mcp_audit.jsonl`.
- O arquivo registra eventos de ciclo do MCP server, resumo dos `new_items` e resultado da tentativa de captura.
- Quando disponivel, tambem registra `mcp_thread_hint_observed` via `message_handler`.
- `SUPERVISOR_MCP_WARNING_CAPTURE=1` habilita fallback de baixo nivel para extrair `threadId` de warnings `codex/event` emitidos pelo SDK quando a notificacao nao e tipada.
- A auditoria e propositalmente resumida (chaves principais e origem candidata), sem despejar blobs enormes.

Eventos de auditoria de continuidade explicita:
- `codex_continue_contract_validation_start`: inicio da validacao de contrato congelado.
- `codex_continue_contract_validation_ok`: contrato validado para o profile ativo.
- `codex_continue_contract_validation_failed`: contrato invalido para o profile ativo.
- `codex_continue_production_profile_blocked`: profile `production` bloqueou execucao sem contrato valido.
- `codex_continue_discovery_start`: inicio da discovery de capability/tool.
- `codex_continue_discovery_result`: resultado da discovery (tool escolhido, campos detectados, score).
- `codex_continue_frozen_contract_selected`: uso do contrato oficial congelado (`codex-reply`).
- `codex_continue_primary_route_selected`: rota deterministica selecionada.
- `codex_continue_fallback_route_selected`: rota heuristica selecionada para compatibilidade.
- `codex_continue_request`: tentativa explicita com `codex_thread_id` (modo `explicit_thread_id`).
- `codex_continue_ack`: rota explicita reconhecida (acknowledged).
- `codex_continue_error`: tentativa explicita sem ack/erro de rota/chamada.
- `codex_continue_fallback`: fallback seguro para continuidade textual quando necessario.
- `codex_continue_strict_mode_blocked_fallback`: modo estrito impediu fallback.

Metadados novos em `state/last_action.json` e checkpoints:
- `codex_continue_attempted`: boolean
- `codex_continue_mode`: `deterministic_primary`, `heuristic_fallback`, `context_fallback`, `not_applicable`
- `codex_continue_status`: `acknowledged`, `fallback_used`, `failed`, `not_applicable`
- `codex_continue_route`: rota efetiva usada (ex.: `call_tool:<tool_name>`)
- `codex_continue_tool_name`: nome do tool usado na tentativa explicita
- `codex_continue_contract_mode`: `deterministic`, `heuristic_fallback`, `context_fallback`, `not_applicable`
- `codex_continue_strict_mode`: `true/false`
- `codex_continue_deploy_profile`: `compat` ou `production`
- `codex_continue_contract_validated`: `true/false`
- `codex_continue_contract_validation_reason`: motivo resumido da validacao

## Continuação futura

- O fluxo atual **nao** muda: `Runner.run(...)` + `SQLiteSession` continua sendo o mecanismo principal do supervisor.
- A continuacao explicita agora tem entrypoint proprio (`--continue-run`) e valida estado persistido minimo.
- O contexto de retomada deixa explicito:
  - `agent_session_id` para continuidade do supervisor (Agents SDK/SQLiteSession)
  - `codex_thread_id` para continuidade explicita no lado Codex (identificador distinto)
- Esses identificadores coexistem e tem papeis diferentes.

## Evolução para Codex App Server

Próxima evolução sugerida:
1. Capturar `codex_thread_id` real do resultado do tool MCP do Codex.
2. Persistir no estado e checkpoints.
3. Implementar continuação explícita no nível do tool com esse identificador.
4. Em etapa posterior, trocar o transporte para App Server mantendo o mesmo workflow.
