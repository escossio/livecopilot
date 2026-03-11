# Project Brain Query (MVP)

## O que faz
`project_brain_query.py` consulta a memoria operacional persistida do projeto (PostgreSQL) para responder perguntas sobre o historico do Livecopilot.

Fonte primaria:
- `project_facts`
- `project_runs`
- `project_memory_chunks`

Sem parsing de markdown como fonte principal.

## Script
- `scripts/project_brain_query.py`
- wrapper operacional recomendado: `scripts/project_brain_query.sh`

Padrao operacional atual:
- use `scripts/project_brain_query.sh` para `semantic/hybrid`.
- uso direto de `project_brain_query.py` fica restrito a diagnostico tecnico/controlado.

## Modos de consulta
- `structured`:
  - consulta `project_facts` e `project_runs` por texto (`title`, `body`, `component`, summaries)
  - ordena priorizando facts `active` e recencia
  - funciona sem embeddings
- `semantic`:
  - consulta `project_memory_chunks` por similaridade vetorial
  - depende de embeddings existentes + `OPENAI_API_KEY` para embedding da query
  - se embeddings nao existem, retorna `semantic_hits=[]` com `semantic_warning` (sem erro)
- `hybrid` (padrao):
  - combina structured + semantic
  - deduplica facts por chave semantica basica
  - retorna resumo consolidado curto

## CLI
Argumentos principais:
- `--project` (default: `livecopilot`)
- `--query` (obrigatorio)
- `--mode structured|semantic|hybrid` (default: `hybrid`)
- `--facts-limit` (default: `10`)
- `--memory-limit` (default: `8`)
- `--format text|json` (default: `text`)

Filtros opcionais:
- `--fact-type`
- `--fact-status`
- `--component`

## Exemplos de uso
Structured por decisao conhecida:
```bash
./scripts/project_brain_query.sh \
  --project livecopilot \
  --query "Separacao question_bank knowledge" \
  --mode structured \
  --format text
```

Hybrid por tema operacional:
```bash
./scripts/project_brain_query.sh \
  --project livecopilot \
  --query "continuidade" \
  --mode hybrid \
  --facts-limit 6 \
  --memory-limit 5 \
  --format text
```

Saida JSON:
```bash
./scripts/project_brain_query.sh \
  --project livecopilot \
  --query "continuidade" \
  --mode hybrid \
  --format json
```

Semantic-only com fallback limpo:
```bash
./scripts/project_brain_query.sh \
  --project livecopilot \
  --query "realtime" \
  --mode semantic \
  --format json
```

Observacao operacional:
- o wrapper carrega `/etc/livecopilot-semantic.env` (quando disponivel) e executa a query como `postgres`, reduzindo warnings de `OPENAI_API_KEY` ausente em `semantic/hybrid`.
- quando ocorrer degradacao, `semantic_warning` agora explicita motivo + caminho recomendado.

## Saida esperada
Texto:
- cabecalho `PROJECT BRAIN RESULT`
- facts relacionados
- runs relacionados
- `summary` curto
- `semantic_warning` quando aplicavel

JSON:
- `related_facts`
- `related_runs`
- `semantic_hits`
- `semantic_warning`
- `summary`

## Limitacoes atuais
- semantic depende de embeddings persistidos em `project_memory_chunks` e `OPENAI_API_KEY` para embedding da query.
- se o banco perder cobertura de embeddings, fallback continua limpo (`semantic_hits=[]` + `semantic_warning`).
- resumo e heuristico (sem modelo externo).
- busca textual ainda e ILIKE/token match simples (sem ranking semantico rico no modo structured).

## Manutencao operacional da camada semantica
Para manter semantic/hybrid sempre atualizados:

```bash
./scripts/maintain_continuity_embeddings.sh --dry-run-only
./scripts/maintain_continuity_embeddings.sh --limit 200 --batch-size 10
```

Com essa rotina, novos chunks sem embedding sao preenchidos incrementalmente sem recriar dados.

Opcionalmente, a manutencao pode ser acoplada ao fechamento da rodada:
```bash
./scripts/round --enable-continuity-hook --enable-embedding-maintenance
```
Assim, apos persistir continuidade e atualizar snapshot/contexto, o closeout tenta preencher faltantes automaticamente.

## Estado atual validado
- `project_memory_chunks`: `with_embedding=30`, `missing_embedding=0`
- `--mode semantic`: retornando `semantic_hits` reais para consultas como `continuidade` e `realtime`
- `--mode hybrid`: combinando hits structured + semantic com evidencias vetoriais

## Avaliacao offline de ranking
Para diagnostico e calibracao orientada por evidencia (sem alterar pesos no proprio comando):

- script: `scripts/eval_project_brain_ranking_offline.py`
- guia: `docs/continuity/PROJECT_BRAIN_RANKING_OFFLINE_EVAL.md`
- bateria inicial: `docs/continuity/examples/project_brain_ranking_eval_queries.json`

Execucao curta:
```bash
./scripts/eval_project_brain_ranking_offline.py --project livecopilot
```
