# Knowledge Pipeline V1

## O que e
`scripts/knowledge_pipeline.sh` e um entrypoint operacional para rodadas controladas de ingestao de conhecimento.

Ele automatiza o fluxo interno:
- plan
- run
- validate

Sem automatizar aquisicao externa ampla.

## O que automatiza
- preview consolidado da rodada por prefixo
- ingestao seletiva por `--source-prefix`
- persistencia semantica seletiva por `--source-prefix`
- validacao minima da rodada
- geracao de artefatos auditaveis em `docs/coverage/`

## O que nao automatiza
- descoberta/coleta remota de fontes
- curadoria automatica ampla
- agendamento autonomo
- reconciliacao opaca de estado

## Contrato da V1

### Entrada
- `--mode plan|run|validate`
- `--source-prefix PREFIX` repetivel e obrigatorio na V1
- `--strict-source-prefix` opcional
- `--round-id` opcional e reutilizavel entre modos

### Modos

#### `plan`
Reaproveita `scripts/round_plan.sh --json`.

Entrega:
- prefixos normalizados
- totais de ingestao e persistencia previstos
- amostra de targets/source_files
- artefato `knowledge_pipeline_plan_<round_id>.json`

Garantia:
- nao altera estado de ingestao nem persistencia

#### `run`
Reaproveita:
- `scripts/ingest_knowledge.sh`
- `app.services.knowledge_ingest --semantic-persist`
- `scripts/with-semantic-env.sh`

Entrega:
- contagens de ingestao executada
- `source_files` resolvidos para persistencia
- `documents_selected`
- `documents_processed`
- `chunks_persisted`
- artefato `knowledge_pipeline_run_<round_id>.json`

Comportamento de previsibilidade:
- executa `plan` interno antes de rodar
- se `--semantic-limit-docs` nao for informado, usa o total previsto no plano
- exige prefixo explicito para evitar rodada ampla acidental

#### `validate`
Reaproveita:
- `scripts/round_plan.sh --json`
- `scripts/utf8_hygiene_scan.sh`
- estado canonico `data/knowledge_index/knowledge_state.json`

Entrega:
- comparacao plano atual vs run
- verificacao de artefatos parsed/chunks no escopo
- resumo do scanner UTF-8
- artefato `knowledge_pipeline_validate_<round_id>.json`

## Artefatos
Padrao default em `docs/coverage/`:
- `knowledge_pipeline_plan_<round_id>.json`
- `knowledge_pipeline_run_<round_id>.json`
- `knowledge_pipeline_validate_<round_id>.json`
- `knowledge_pipeline_validate_utf8_<round_id>.json`

## Como evita side-effects inesperados
- V1 exige `--source-prefix` explicito
- `plan` so usa preview/dry-run/list-targets
- `validate` nao reingere nem repersiste; apenas valida e gera artefatos
- `run` calcula o escopo antes de executar e registra o escopo resolvido

## Uso

### Rodada recomendada

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
  --semantic-embedding-mode mock

./scripts/knowledge_pipeline.sh \
  --mode validate \
  --round-id "$ROUND_ID" \
  --source-prefix continuity_docs_selected/
```

### Strict mode

```bash
./scripts/knowledge_pipeline.sh \
  --mode plan \
  --source-prefix nao_existe/ \
  --strict-source-prefix
```

## Fluxo recomendado
1. rodar `plan`
2. inspecionar o artefato e os totais previstos
3. rodar `run`
4. rodar `validate`
5. registrar checkpoint e handoff

## Extensao V2
Para a validacao semantica minima por rodada/prefixo, veja `docs/KNOWLEDGE_PIPELINE_V2_SEMANTIC_VALIDATE.md`.
