# Knowledge Pipeline V2 Semantic Validate

## O que e
V2 minima de validacao semantica por rodada/prefixo em cima da knowledge pipeline V1.

Ela verifica se o conteudo persistido no escopo da rodada esta minimamente recuperavel por busca semantica.

## O que valida
- queries de smoke simples e auditaveis
- se o `top1` cai no documento esperado com frequencia minima
- se o `topk` contem o documento esperado para todas as queries
- se a rodada continua semanticamente consultavel com o mesmo `embedding_mode` usado no `run`
- ranking semantico dentro do escopo da rodada (`round_scope_only`)

## O que nao valida
- qualidade global do corpus
- cobertura tematica profunda
- ranking fino entre documentos proximos
- lacunas cognitivas complexas

## Interface escolhida
Modo novo e separado no pipeline:

```bash
./scripts/knowledge_pipeline.sh \
  --mode semantic-validate \
  --round-id <round_id> \
  --source-prefix continuity_docs_selected/
```

Motivo:
- preserva o `validate` operacional da V1
- deixa a camada semantica explicita e auditavel
- evita misturar verificacao estrutural com smoke cognitivo

## Como as queries sao definidas

### Padrao V2
Sem arquivo externo, as queries sao derivadas dos `source_files` da rodada:
- prioridade para arquivos fora de `HANDOFF_*`
- a query nasce do nome do arquivo
- timestamps e tokens genericos sao removidos
- exemplo:
  - `SEMANTIC_ROUND_CLOSEOUT_CHECKLIST.md` -> `semantic closeout checklist`
  - `UTF8_HYGIENE_SCANNER.md` -> `utf8 hygiene scanner`

### Opcional
Tambem aceita queryset explicito:

```bash
./scripts/knowledge_pipeline.sh \
  --mode semantic-validate \
  --round-id <round_id> \
  --source-prefix continuity_docs_selected/ \
  --semantic-queryset-file docs/coverage/meu_queryset.json
```

Formato aceito:
- lista de strings
- ou objeto com `queries`
- cada item pode conter `query` e `expected_source_file`

## Criterio minimo de sucesso
Artefato registra:
- `total_queries`
- `top1_expected_prefix_count`
- `topk_expected_prefix_count`
- `top1_expected_source_file_count`
- `topk_expected_source_file_count`
- `semantic_smoke_passed`

Regra V2:
- todas as queries precisam ter o `expected_source_file` em `topk`
- pelo menos metade das queries precisa ter `top1` igual ao `expected_source_file`

## Escopo da busca
- a V2 ranqueia candidatos apenas dentro do escopo da rodada/prefixo
- isso evita ruido do corpus inteiro e deixa a validacao mais previsivel
- portanto ela mede recuperabilidade semantica **do recorte ingerido**, nao competicao global entre prefixos

## Observacao sobre embedding mode
- `openai` produz a validacao semantica real da V2
- `mock` continua suportado para trilha tecnica/auditavel, mas nao deve ser interpretado como prova cognitiva forte

## Artefato
Gerado em `docs/coverage/`:
- `knowledge_pipeline_semantic_validate_<round_id>.json`

Conteudo minimo:
- `round_id`
- `source_prefixes`
- `queries`
- `results`
- `aggregate`
- `semantic_smoke_passed`

## Interpretacao
- `semantic_smoke_passed=true`:
  - smoke semantico minimo passou para a rodada
- `topk_expected_prefix_count < total_queries`:
  - ha queries sem hit relevante nem no escopo esperado
- `top1_expected_prefix_count` baixo:
  - o conteudo pode existir, mas o ranking ainda nao esta convincente
