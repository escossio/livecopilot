# ROUND SUMMARY - CONTINUITY REAL FLOW HOOK

## status final
success

## objetivo da rodada
Conectar a cadeia de continuidade ao ponto real de fim de rodada do fluxo operacional, mantendo reversibilidade e fallback manual.

## ponto real escolhido
- fechamento de rodada do `codex-supervisor` apos escrita de:
  - `state/last_action.json` (fonte estruturada primaria),
  - `STATUS.md` e `.supervisor/checkpoints/...` no projeto alvo.

## implementacao
- script criado: `scripts/run_real_round_flow.sh`
- modo padrao:
  1. executa rodada no `codex-supervisor` (`run-once` ou `continue-run`),
  2. le `last_action.json` (sem parsing de markdown livre),
  3. quando hook habilitado, chama `scripts/run_round_closeout.sh`.
- modo de replay estruturado:
  - `--from-last-action-only` reutiliza ultimo `last_action.json` para ambientes sem execucao imediata do supervisor.

## ativacao/desativacao
- ativacao por flag: `--enable-continuity-hook`
- ativacao por env var: `LIVECOPILOT_CONTINUITY_HOOK=1`
- desativacao explicita: `--disable-continuity-hook`

## validacao local (obrigatoria)
1. Fluxo real bridge sem hook:
   - `./scripts/run_real_round_flow.sh --from-last-action-only --disable-continuity-hook --mode run-once`
   - resultado: comportamento normal, sem cadeia de continuidade.
2. Fluxo real bridge com hook:
   - `./scripts/run_real_round_flow.sh --from-last-action-only --enable-continuity-hook --mode run-once ...`
   - resultado: payload + ingest + snapshot txt/json + contexto final.
3. Artefatos confirmados:
   - `docs/continuity/payloads/*.json`
   - `docs/continuity/bootstrap/latest_snapshot.txt`
   - `docs/continuity/bootstrap/latest_snapshot.json`
   - `docs/continuity/opening_context/latest_new_chat_context.txt`
4. Idempotencia:
   - `run_key=run_f3af7f3c1a4a40952278d088`
   - `count(project_runs where run_key)=1`

## limitacoes atuais
- execucao completa do `codex-supervisor` continua dependente de ambiente com `OPENAI_API_KEY`.
- no ambiente local com PostgreSQL `peer`, o closeout usa fallback (build local + ingest como `postgres`).
