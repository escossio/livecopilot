# Handoff Pipeline Lab — validação do acesso

## O que foi feito
- o script `scripts/start-pipeline-lab.sh` agora dispara `.venv/bin/python3 -m uvicorn app.main:app` e `.venv/bin/python3 -m http.server 8090` dentro de `setsid`, garantindo que a API/UI permaneçam em background depois que o shell fecha.
- `scripts/status-pipeline-lab.sh` segue sendo a forma rápida de conferir listeners, PIDs e códigos HTTP.

## Comandos executados nesta validação
1. `bash scripts/start-pipeline-lab.sh` (levanta API e UI via setsid e informa PIDs/URLs e logs em `/tmp/pipeline-lab-*.log`).
2. `curl http://127.0.0.1:8000/api/runs` e `curl http://127.0.0.1:8090` (confirmou endpoints locais).
3. `curl http://10.45.0.3:8000/api/runs` e `curl http://10.45.0.3:8090` (confirmou que a rede responde).
4. `ss -tulnp | grep -E '8000|8090'` (confirma listeners em `0.0.0.0`).

## Resultados
- API + UI respondem em `0.0.0.0:8000/8090` e via IP `10.45.0.3`, permitindo testes no celular.
- Logs iniciais em `/tmp/pipeline-lab-api.log`/`/tmp/pipeline-lab-ui.log` mostram o servidor iniciando normalmente.

## URLs finais para teste
- API base: `http://10.45.0.3:8000/api`
- UI: `http://10.45.0.3:8090/`
