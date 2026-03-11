# ROUND SUMMARY - CONTINUITY FLOW CONSOLIDATION

## estado anterior
- continuidade funcional, mas ainda com atrito operacional em dois pontos:
  1. operador precisava lembrar flags para ligar hook no fluxo real;
  2. consultas `semantic/hybrid` podiam cair em warning de `OPENAI_API_KEY` ausente quando executadas diretamente como `postgres`.
- no closeout, ambiente `peer` gerava tentativa inicial com erro antes do fallback.

## diagnostico confirmado
- fluxo real:
  - `scripts/round` delegava para `scripts/run_real_round_flow.sh`, mas nao ligava hook por padrao.
- ambiente de chave:
  - fonte canonica existe: `/etc/livecopilot-semantic.env` (permissao `600 root:root`);
  - `runuser -u postgres` nao consegue ler esse arquivo diretamente;
  - por isso `project_brain_query.py` chamado como `postgres` sem repasse explicito de env entrava em warning.
- PostgreSQL local:
  - `pg_hba.conf` usa `peer` para conexoes locais (`local all postgres peer`, `local all all peer`);
  - apenas role `postgres` existe no banco;
  - usuario efetivo do operador no ambiente: `root`;
  - logo, chamadas diretas ao DB como root falham por peer e exigem execucao como `postgres`.

## correcoes aplicadas (minimas e reversiveis)
1. `scripts/round`:
   - passa a habilitar por padrao:
     - `--enable-continuity-hook`
     - `--enable-embedding-maintenance`
   - override preservado por:
     - `--disable-continuity-hook`
     - `--disable-embedding-maintenance`
2. `scripts/run_round_closeout.sh`:
   - em root + `peer` sem DSN explicito, usa diretamente build local + ingest como `postgres`, evitando erro inicial recorrente.
3. `scripts/project_brain_query.sh` (novo):
   - wrapper operacional que carrega `/etc/livecopilot-semantic.env` e executa query como `postgres` com env repassado.
4. `scripts/smoke_openai_embedding.sh`:
   - remove chave hardcoded e passa a usar `/etc/livecopilot-semantic.env`.

## evidencias de validacao
- fluxo real sem hook:
  - `./scripts/round --from-last-action-only --disable-continuity-hook`
  - resultado: `[real-flow] ... continuidade desabilitada`.
- fluxo real padrao (sem lembrar flag):
  - `./scripts/round --from-last-action-only --summary-short ... --summary-full ... --checkpoint-path STATUS.md --facts-file ...`
  - resultado:
    - closeout executado;
    - persistencia de continuidade OK (`run_id=17`, `run_key=run_a1a80531a2135c87e6479587`);
    - snapshot/contexto atualizados;
    - embedding maintenance executada e `missing_embedding=0`.
- idempotencia:
  - reexecucao com mesmos argumentos manteve `count(project_runs where run_key='run_a1a80531a2135c87e6479587')=1`.
- semantic/hybrid:
  - chamada direta antiga (`runuser -u postgres ... project_brain_query.py`) ainda mostra `semantic_warning` por falta de chave no ambiente do processo;
  - wrapper novo (`./scripts/project_brain_query.sh ...`) retorna `semantic_warning=null` e `semantic_hits` preenchido.

## comandos de validacao usados
```bash
bash -n scripts/round
bash -n scripts/run_round_closeout.sh
bash -n scripts/project_brain_query.sh

./scripts/round --from-last-action-only --disable-continuity-hook

./scripts/round --from-last-action-only \
  --summary-short "Consolidacao fluxo real default hook" \
  --summary-full "Rodada curta para validar default hook + embedding maintenance no launcher round" \
  --checkpoint-path STATUS.md \
  --facts-file docs/continuity/examples/sample_facts.json

runuser -u postgres -- psql -d livecopilot -At -c \
  "SELECT count(*) FROM project_runs WHERE run_key='run_a1a80531a2135c87e6479587';"

./scripts/project_brain_query.sh --project livecopilot --query "continuidade" --mode hybrid --format json
./scripts/project_brain_query.sh --project livecopilot --query "realtime" --mode semantic --format json

runuser -u postgres -- psql -d livecopilot -c \
  "SELECT COUNT(*) total_chunks, COUNT(*) FILTER (WHERE embedding IS NOT NULL) with_embedding, COUNT(*) FILTER (WHERE embedding IS NULL) missing_embedding FROM project_memory_chunks;"
```

## pendencias
- dependencia de `runuser -u postgres` permanece no ambiente local com `peer` + role unica `postgres`.
- endurecimento adicional (ex.: role operacional dedicada + DSN com scram local) ainda nao foi aplicado nesta rodada para evitar impacto amplo.
