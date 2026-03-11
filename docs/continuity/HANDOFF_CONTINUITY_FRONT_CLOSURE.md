# HANDOFF - CONTINUITY FRONT CLOSURE

## objetivo da frente
Consolidar a continuidade no fluxo operacional real do Livecopilot, com persistencia auditavel, bootstrap/contexto de abertura de chat e trilho operacional estavel para consulta semantica.

## entregas concluidas
- continuidade integrada ao fechamento de rodada no fluxo real, com controle reversivel (hook/opt-out).
- `scripts/round` estabelecido como entrypoint operacional padrao.
- payload canonico + ingest + snapshot + contexto final funcionando de ponta a ponta.
- manutencao incremental de embeddings integrada ao closeout (com controle explicito).
- wrapper operacional oficial para consultas: `scripts/project_brain_query.sh`.
- smokes dedicados:
  - `scripts/smoke_round_continuity_default.sh`
  - `scripts/smoke_project_brain_query_wrapper.sh`
- observabilidade de degradacao semantica reforcada (`semantic_warning` com motivo + recomendacao).

## criterios de validacao que passaram
- round padrao com closeout e continuidade: OK.
- persistencia confirmada em `project_runs`, `project_facts`, `project_memory_chunks`: OK.
- geracao/atualizacao de snapshot e contexto final: OK.
- consulta semantic/hybrid via wrapper com `semantic_warning=null`: OK.
- `missing_embedding=0` no escopo validado pelos smokes: OK.

## divida aceita
- ambiente PostgreSQL local permanece com `peer auth` + role unica `postgres`.
- operacao local segue dependente de `runuser -u postgres` para alguns passos.
- decisao consciente: nao alterar estrutura de autenticacao/roles nesta frente.

## proximas frentes possiveis
1. frente de infraestrutura DB: role operacional dedicada + DSN local com autenticacao apropriada (reduzir dependencia de `runuser`).
2. frente de operacionalizacao: agendar os smokes em rotina curta (cron/pipeline leve).
3. frente de UX operacional: padronizar wrappers equivalentes para todos os comandos semanticos legados.
