# GPT Tool Host Contract

Contrato formal do wrapper local `supervisor.gpt_tool_host` para integração com runtime de GPT no ambiente local.

## Tool Name

- Nome lógico: `codex-supervisor-gpt-tool-host`
- Comando: `python3 -m supervisor.gpt_tool_host`

## Execução

```bash
python3 -m supervisor.gpt_tool_host [opções]
```

## Argumentos

- `--base-url` (default: `http://127.0.0.1:8787`)
- `--token` (opcional; se omitido tenta `SUPERVISOR_API_TOKEN`)
- `--timeout` (default: `30.0`)
- `--force-mode` (`run_once` ou `continue_run`, default: automático)
- `--target-project-path` (default: vazio)
- `--session-id` (default: vazio)

## Credencial (token)

Fontes suportadas, em ordem de precedência:
1. `--token` (quando informado explicitamente)
2. variável de ambiente `SUPERVISOR_API_TOKEN`
3. `None` (sem token)

Recomendação operacional:
- preferir `SUPERVISOR_API_TOKEN` via ambiente para reduzir exposição em CLI/histórico/logs.
- manter `--token` apenas para compatibilidade ou uso excepcional.

Exemplos:

```bash
export SUPERVISOR_API_TOKEN=<TOKEN>
python3 -m supervisor.gpt_tool_host
python3 -m supervisor.gpt_tool_host --force-mode continue_run
python3 -m supervisor.gpt_tool_host --force-mode run_once --target-project-path /lab/projects/<repo_alvo>
python3 -m supervisor.gpt_tool_host --base-url http://127.0.0.1:8787 --timeout 30
python3 -m supervisor.gpt_tool_host --token <TOKEN>
```

## Decisão automática

Quando `--force-mode` não é enviado:

- usa `continue_run` se `status.can_continue == true` e `status.codex_thread_id` presente
- caso contrário usa `run_once`

## Saída JSON (stdout)

`stdout` contém apenas JSON (uma linha), sem texto adicional.

Campos de resposta:

- `ok` (`boolean`)
- `decision` (`"run_once" | "continue_run" | null`)
- `execution_result` (`object | null`)
- `last_action` (`object | null`)
- `next_step` (`string | null`)
- `status_snapshot` (`object | null`)
- `error` (`object | null`)

Estrutura de `error`:

- `error.kind` (`string`)
- `error.message` (`string`)
- `error.details` (`object`)

## Tipos de erro esperados

- `http_error`: API respondeu com erro HTTP (inclui `status_code` e `response_body` em `details`)
- `client_error`: falha de conexão/time-out/JSON inválido no cliente
- `host_error`: erro no host wrapper (ex.: argumentos inválidos)
- `unexpected_error`: falha não classificada no adaptador

## Payload esperado (sucesso)

```json
{
  "ok": true,
  "decision": "continue_run",
  "execution_result": {
    "status": "success"
  },
  "last_action": {
    "status": "success"
  },
  "next_step": "Proximo passo sugerido pelo agente: ...",
  "status_snapshot": {
    "can_continue": true,
    "codex_thread_id": "019cbc90-..."
  }
}
```

## Payload esperado (erro)

```json
{
  "ok": false,
  "decision": null,
  "execution_result": null,
  "last_action": null,
  "next_step": null,
  "status_snapshot": null,
  "error": {
    "kind": "client_error",
    "message": "Request failed for GET /status: [Errno 111] Connection refused",
    "details": {}
  }
}
```

## Integração via subprocess

```python
import json
import subprocess

proc = subprocess.run(
    ["python3", "-m", "supervisor.gpt_tool_host", "--force-mode", "continue_run"],
    capture_output=True,
    text=True,
    check=False,
)
payload = json.loads(proc.stdout)
if payload["ok"]:
    decision = payload["decision"]
    next_step = payload["next_step"]
else:
    err_kind = payload["error"]["kind"]
    err_msg = payload["error"]["message"]
```

## Regras de consumo recomendadas

- Sempre parsear `stdout` como JSON.
- Confiar em `ok` como gate principal.
- Em `ok=false`, tratar por `error.kind`.
- Não depender de texto livre fora da estrutura JSON.
- Quando decidir por `run_once`, sempre enviar `--target-project-path` explícito.
- Padrão recomendado de alvo neste ambiente: `/lab/projects/livecopilot`.
- Nunca usar raiz agregadora como alvo (`/lab/projects` ou `/lab`), pois o backend bloqueia com erro HTTP `400`.
