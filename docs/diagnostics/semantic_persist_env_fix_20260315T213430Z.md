# Semantic persist environment fix · 2026-03-15T21:34Z

## Diagnóstico
- o `scripts/with-semantic-env.sh` usa `/usr/bin/python3` com `/etc/livecopilot-semantic.env`, que define `DATABASE_URL/SEMANTIC_PG_DSN` apontando para `postgresql://livecopilot_app@127.0.0.1:5432/livecopilot`.
- o `--semantic-persist` importava `psycopg` (não `psycopg2`), portanto o fluxo caiu com `ModuleNotFoundError: No module named 'psycopg'`.
- ao tentar instalar via `pip --user` o ambiente reportou `externally-managed-environment`, então foi necessário instalar o driver por pacote Debian.

## Correção aplicada
- `apt-get install -y python3-psycopg` adicionou `psycopg 3.2.6` + binário C para o interpreter no `/usr/bin/python3`.
- `apt-get install -y python3-openai` trouxe `python3-pydantic*`, `python3-tqdm`, `python3-distro`, `python3-annotated-types` e `openai 1.69.0`, garantindo que o mesmo interpreter usado pelo semantic-persist importe o cliente OpenAI quando o key está presente.
- validação:
  - `scripts/with-semantic-env.sh python3 -c "import psycopg; print(psycopg.__version__)"` → `3.2.6`
  - `scripts/with-semantic-env.sh python3 -c "import openai; print(openai.__version__)"` → `1.69.0`

## Observação
- a persistência foi reexecutada com `--semantic-embedding-mode mock` para evitar gerar milhares de chamadas OpenAI e garantir que o índice vetorial refletisse os chunks limpos antes de revalidar o subset.
