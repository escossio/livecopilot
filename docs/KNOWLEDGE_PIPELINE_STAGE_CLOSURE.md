# Knowledge Pipeline Stage Closure

## Visao geral da frente
A frente "Knowledge Pipeline" entregou um fluxo operacional auditavel para rodadas controladas de conhecimento no LIVEcopilot, cobrindo:
- planejamento da rodada
- execucao de ingestao seletiva
- persistencia semantica seletiva
- validacao estrutural
- validacao semantica minima por rodada/prefixo

O foco desta etapa foi deixar o fluxo `plan -> run -> validate -> semantic-validate` previsivel, reutilizavel e com evidencia objetiva.

## Entregas concluidas

### V1 operacional
- entrypoint:
  - `scripts/knowledge_pipeline.sh`
- modos V1:
  - `plan`
  - `run`
  - `validate`
- documentacao:
  - `docs/KNOWLEDGE_PIPELINE_V1.md`
- contrato coberto por teste:
  - `tests/test_knowledge_pipeline_cli_contract.py`

### V2 de validacao semantica
- extensao do entrypoint:
  - `scripts/knowledge_pipeline.sh --mode semantic-validate`
- helper:
  - `scripts/knowledge_pipeline_semantic_validate.py`
- documentacao:
  - `docs/KNOWLEDGE_PIPELINE_V2_SEMANTIC_VALIDATE.md`
- contrato coberto por teste:
  - `tests/test_knowledge_pipeline_semantic_validate.py`

## Modos disponiveis hoje
- `plan`
  - consolida preview da rodada por prefixo sem side-effects
- `run`
  - executa ingestao seletiva + persistencia semantica seletiva
- `validate`
  - valida escopo, artefatos parsed/chunks e scanner UTF-8
- `semantic-validate`
  - roda smoke semantico auditavel dentro do escopo da rodada

## Artefatos gerados por rodada
Em `docs/coverage/`:
- `knowledge_pipeline_plan_<round_id>.json`
- `knowledge_pipeline_run_<round_id>.json`
- `knowledge_pipeline_validate_<round_id>.json`
- `knowledge_pipeline_validate_utf8_<round_id>.json`
- `knowledge_pipeline_semantic_validate_<round_id>.json`

## O que ja foi validado em caso real
- V1:
  - prefixo `continuity_docs_selected/`
  - fluxo `plan -> run -> validate`
  - artefatos e validacao operacional OK
- V2:
  - prefixo `terraform_docs_selected_incremental/`
  - `embedding_mode=openai`
  - `semantic_smoke_passed=true`
- dogfooding adicional:
  - prefixo `codex_docs_selected/`
  - recorte controlado do repo oficial `openai/codex`
  - recuperabilidade operacional real confirmada para queries de instalacao, autenticacao, configuracao, sandbox, execution policy e slash commands

## Como usar hoje
```bash
ROUND_ID="$(date -u +%Y%m%dT%H%M%SZ)"

./scripts/knowledge_pipeline.sh \
  --mode plan \
  --round-id "$ROUND_ID" \
  --source-prefix continuity_docs_selected/

./scripts/knowledge_pipeline.sh \
  --mode run \
  --round-id "$ROUND_ID" \
  --source-prefix continuity_docs_selected/ \
  --semantic-embedding-mode openai

./scripts/knowledge_pipeline.sh \
  --mode validate \
  --round-id "$ROUND_ID" \
  --source-prefix continuity_docs_selected/

./scripts/knowledge_pipeline.sh \
  --mode semantic-validate \
  --round-id "$ROUND_ID" \
  --source-prefix continuity_docs_selected/
```

## Limites atuais
- nao automatiza aquisicao externa ampla
- nao faz avaliacao global de qualidade do corpus
- a V2 mede `round_scope_only`, nao competicao global entre prefixos
- `mock` continua util para trilha tecnica, mas nao substitui validacao cognitiva real
- em prefixos novos, o auto-limit do `run` pode precisar endurecimento para evitar primeira execucao subdimensionada

## Riscos e pendencias nao bloqueantes
- parte dos recortes reais pode apontar para documentacao remota oficial e, portanto, nao carregar profundidade completa localmente
- o valor do pipeline depende de queryset explicito em rodadas mais importantes
- ha espaco para endurecer ainda mais a ergonomia de closeout por rodada, mas isso nao bloqueia o estado atual

## Contratos e testes existentes
- `tests/test_knowledge_pipeline_cli_contract.py`
  - blinda contrato minimo de `plan` e `validate`
- `tests/test_knowledge_pipeline_semantic_validate.py`
  - blinda derivacao de queries e contrato minimo do smoke semantico
- `./scripts/unit_test_gate.sh`
  - inclui a trilha da knowledge pipeline no gate local

## Decisao de encerramento
Esta frente esta formalmente encerrada no estado atual.

Motivo:
- V1 operacional entregue e documentada
- V2 minima entregue e documentada
- testes de contrato existentes
- gate local cobrindo a trilha
- caso real com `semantic_smoke_passed=true` ja executado

## Proxima evolucao natural
Quando esta frente for retomada, a evolucao natural e uma V3 pequena e focada em qualidade de validacao:
- queryset explicito versionado por dominio/prefixo
- endurecimento do auto-limit para prefixos novos
- auditoria curta opcional de ranking fora de `round_scope_only`

Isso fica explicitamente fora desta rodada de fechamento.
