# Handoff Pipeline Lab — acesso de teste

## Como subir a API
- ative o venv local (`. .venv/bin/activate`), depois rode `uvicorn app.main:app --host 0.0.0.0 --port 8000` para expor `/api/runs`, `/api/runs/{id}` e `/api/runs/{id}/next`.
- o `app/main.py` usa o módulo `app.api.routes` já existente, então não há duplicação de lógica.

## Como subir a UI
- execute `python3 -m http.server 8090 --directory web` dentro de `lab/projects/pipeline-lab` para servir a interface estática.
- o `web/app.js` aponta para a API em `http://127.0.0.1:8000/api`, então basta abrir `http://127.0.0.1:8090/` no navegador.

## URLs finais de acesso
- API: `http://127.0.0.1:8000/api`
- UI: `http://127.0.0.1:8090/`

## Validações executadas
- `curl http://127.0.0.1:8000/api/runs` (confirmou JSON serializado da store)
- `curl http://127.0.0.1:8090` (confirmou que a UI carrega o HTML/JS)

## Primeiro domínio recomendado para testar manualmente
- `terraform` (já possui runs e artefatos registrados e aparece imediatamente no cockpit).
