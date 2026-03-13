# ROADMAP

## Estado atual

- Core local funcional: realtime + knowledge + question bank + gap analysis.
- Operacao com evidencias e handoffs recorrentes em `docs/`.
- Busca externa governada em estado parcial (contrato pronto, evolucao funcional controlada).

## Frentes concluidas recentemente

- Hardening de ingestao seletiva por prefixo (`--source-prefix`, `--strict-source-prefix`).
- Persistencia semantica seletiva por prefixo.
- Refatoracao da resolucao de prefixo para modulo reutilizavel.
- Comando unificado de planejamento por prefixo (`scripts/round_plan.sh`).
- Blindagem de contrato com testes dedicados e integracao ao gate local.

Evidencias:
- `docs/HANDOFF_PREFIX_INGEST_HARDENING_20260312T193121Z.md`
- `docs/HANDOFF_PREFIX_SEMANTIC_PERSIST_20260312T194126Z.md`
- `docs/HANDOFF_PREFIX_RESOLUTION_REFACTOR_20260312T200733Z.md`
- `docs/HANDOFF_ROUND_PLAN_PREFIX_MODE_20260312T213700Z.md`
- `docs/HANDOFF_ROUND_PLAN_CONTRACT_TESTS_20260312T214600Z.md`

## Proximas frentes relevantes

- Finalizar curadoria local para preparacao GitHub/remoto.
- Consolidar CI minimo para validar gate local em PR.
- Reduzir drift entre estado operacional e inventario versionado.
- Evoluir observabilidade de qualidade (latencia, relevancia e cobertura de gaps).

## Backlog de medio prazo

- Evolucao controlada da busca externa com governanca (sem degradar o core local-first).
- Melhor acoplamento entre contexto realtime e ranking semantico.
- Fortalecer contratos de teste para CLIs operacionais adicionais.
- Organizar politicas de contribuicao e seguranca com fluxo de triagem mais formal.

## Visao de evolucao

- Manter o eixo principal do produto em copiloto contextual realtime com base tecnica auditavel.
- Tratar runbook/ops e busca externa como extensoes governadas do nucleo.
- Priorizar progresso incremental com evidencia objetiva em `STATUS.md` e handoffs por rodada.
