# Handoff Pipeline Lab — correção de acesso recusado

## Causa do problema
- As portas 8000 e 8090 estavam livres, mas nenhum servidor estava escutando nelas, por isso qualquer cliente na rede recebia `ERR_CONNECTION_REFUSED`.

## Comandos finais que funcionaram
- API: `. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- UI: `python3 -m http.server 8090 --bind 0.0.0.0 --directory web`

## Validação local
- `curl http://127.0.0.1:8000/api/runs` retornou as duas runs registradas.
- `curl http://127.0.0.1:8090` trouxe o HTML do cockpit e o JavaScript apontando para a API.

## Validação via rede
- `curl http://10.45.0.3:8000/api/runs` funcionou, mostrando JSON completo da store.
- `curl http://10.45.0.3:8090` retornou o mesmo HTML da UI.
- `ss -tulnp | grep -E '8000|8090'` confirmou listeners em `0.0.0.0:8000` (uvicorn) e `0.0.0.0:8090` (http.server).

## Scripts criados
- `scripts/start-pipeline-lab.sh`: ativa o venv, inicia API/UI com `nohup`, registra `/tmp/pipeline-lab-api.log` e `/tmp/pipeline-lab-ui.log`, exibe PIDs/URLs.
- `scripts/status-pipeline-lab.sh`: lista listeners, processos relevantes e faz curls rápidos para API/UI.

## URLs finais para testes em rede
- API: `http://10.45.0.3:8000/api`
- UI: `http://10.45.0.3:8090/`
