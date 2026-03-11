# ROUND SUMMARY - CONTINUITY FINAL HARDENING

## estado anterior
- cadeia de continuidade ja funcional e integrada ao closeout real.
- `scripts/round` ja habilitava continuidade + embedding maintenance por padrao.
- bloqueio operacional residual: referencias antigas ao uso direto de `project_brain_query.py` e ausencia de smoke scripts dedicados para rotina diaria.

## padronizacao oficial consolidada
1. fluxo de rodada operacional:
- comando oficial: `./scripts/round`
- continuidade + embedding maintenance ligados por padrao
- opt-out explicito:
  - `./scripts/round --disable-continuity-hook`
  - `./scripts/round --disable-embedding-maintenance`

2. consulta operacional do brain:
- comando oficial: `./scripts/project_brain_query.sh`
- uso direto de `scripts/project_brain_query.py` restrito a diagnostico tecnico/controlado.

3. observabilidade de degradacao semantica:
- `semantic_warning` agora explicita:
  - motivo da degradacao
  - caminho operacional recomendado (`scripts/project_brain_query.sh` e/ou manutencao de embeddings)

## endurecimento aplicado
- adicionados smokes operacionais repetiveis:
  - `scripts/smoke_round_continuity_default.sh`
  - `scripts/smoke_project_brain_query_wrapper.sh`
- documentacao operacional atualizada para apontar wrapper como caminho oficial e incluir os smokes.

## validacao rapida da continuidade
```bash
./scripts/smoke_round_continuity_default.sh
```
Valida objetivamente:
- execucao de round + closeout
- persistencia em `project_runs`, `project_facts`, `project_memory_chunks`
- atualizacao de snapshots/contexto final
- `missing_embedding=0` para o run validado

## validacao rapida do brain query operacional
```bash
./scripts/smoke_project_brain_query_wrapper.sh
```
Valida objetivamente:
- execucao via wrapper operacional
- `semantic_warning=null` em `hybrid` e `semantic`
- `semantic_hits` preenchido no cenario validado

## pendencia aceita (postgres)
- dependencia estrutural mantida nesta rodada:
  - autenticacao local PostgreSQL via `peer`
  - role unica `postgres`
  - execucao operacional com `runuser -u postgres`
- decisao: manter como divida tecnica explicitamente aceita para evitar mudanca estrutural de banco nesta rodada.

## proximos passos recomendados (sem refactor amplo)
1. adicionar smoke em pipeline/cron local de operacao (execucao periodica curta).
2. padronizar wrappers equivalentes para outros comandos semanticos legados que ainda dependam de env + `postgres`.
3. planejar rodada separada para role operacional dedicada no PostgreSQL (fora deste escopo).
