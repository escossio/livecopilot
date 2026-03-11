# ROUND SUMMARY - CONTINUITY HOOK

## status final
success

## objetivo da rodada
Adicionar ponto de integracao opcional da cadeia de continuidade no encerramento operacional da rodada, sem quebrar o modo manual.

## implementacao
- script criado: `scripts/run_round_closeout.sh`
- comportamento com hook desabilitado (default): no-op seguro
- comportamento com hook habilitado:
  1. persistencia de continuidade (`run_continuity_capture.sh`)
  2. snapshot JSON atualizado (`new_chat_context.sh --format json`)
  3. snapshot TXT + contexto final atualizados (`new_chat_context.sh --format txt`)
- fallback `peer` no hook:
  - se `run_continuity_capture.sh` falhar por autenticacao local, o wrapper executa:
    1. `continuity_build_payload.py` como usuario atual
    2. `continuity_ingest.py` como `postgres`
  - objetivo: manter integracao sem exigir permissao de escrita do `postgres` em `docs/continuity/payloads/`.

## ativacao/desativacao
- ativacao por flag: `--enable-continuity-hook`
- ativacao por env var: `LIVECOPILOT_CONTINUITY_HOOK=1`
- desativacao explicita: `--disable-continuity-hook`

## artefatos esperados com hook habilitado
- `docs/continuity/payloads/*.json`
- `docs/continuity/bootstrap/latest_snapshot.json`
- `docs/continuity/bootstrap/latest_snapshot.txt`
- `docs/continuity/opening_context/latest_new_chat_context.txt`

## validacao da rodada
- fluxo sem hook: OK (sem alterar cadeia atual)
- fluxo com hook: OK (persistencia + snapshot + contexto final)
- reexecucao controlada: sem duplicacao indevida de run para mesma rodada (idempotencia por `run_key`)
- evidencia local:
  - `run_key=run_f479dd286cc164a96e7757dd`
  - `count(project_runs where run_key)=1`
  - artefatos atualizados em `payloads/`, `bootstrap/` e `opening_context/`

## limitacoes atuais
- para DB com autenticacao `peer`, fallback para execucao como `postgres` depende de `runuser` e root
- hook e opcional; nao existe acoplamento obrigatorio no loop principal
