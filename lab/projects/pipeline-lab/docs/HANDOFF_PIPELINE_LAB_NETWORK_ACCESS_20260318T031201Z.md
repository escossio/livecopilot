# Handoff Pipeline Lab — acesso em rede local

## Como subir os serviços
- API: ative o venv (`. .venv/bin/activate`) e execute `uvicorn app.main:app --host 0.0.0.0 --port 8000`; o FastAPI expõe `/api/runs`, `/api/runs/{id}` e `/api/runs/{id}/next` com CORS liberado para a UI.
- UI: rode `python3 -m http.server 8090 --bind 0.0.0.0 --directory web` na raiz do projeto para servir `web/index.html` que consome `http://127.0.0.1:8000/api`.

## Validações realizadas
- Localmente: `curl http://127.0.0.1:8000/api/runs`, `curl http://127.0.0.1:8090`.
- Via rede: `curl http://10.45.0.3:8000/api/runs`, `curl http://10.45.0.3:8090`.
- `ss -tulnp` confirma listeners em `0.0.0.0:8000` (uvicorn) e `0.0.0.0:8090` (http.server).

## URLs finais para testes manuais
- API base: `http://10.45.0.3:8000/api`
- UI: `http://10.45.0.3:8090/`

## Observações
- O host 10.45.0.3 já responde nos testes de curl, então qualquer dispositivo na mesma rede deve conseguir carregar o cockpit com os endpoints API listados acima.
- Bloqueios de firewall não foram detectados; se o celular não conectar, recomende verificar o firewall do host.
