# ROUND SUMMARY - PROJECT BRAIN QUERY

## status final
success

> Nota historica: os comandos abaixo registram a validacao inicial do MVP. No fluxo operacional atual, o caminho oficial e `scripts/project_brain_query.sh`.

## objetivo
Criar um utilitario de consulta da memoria operacional do projeto para responder perguntas sobre o historico do Livecopilot.

## entrega tecnica
- script novo: `scripts/project_brain_query.py`
- modos suportados:
  - `structured`
  - `semantic`
  - `hybrid` (padrao)
- saida suportada:
  - `text`
  - `json`
- filtros opcionais:
  - `--fact-type`
  - `--fact-status`
  - `--component`

## comportamento implementado
- `structured`:
  - consulta facts/runs no banco por texto (sem depender de embeddings)
  - token matching + frase para reduzir falso negativo de query
  - prioriza facts ativos e recentes
- `semantic`:
  - busca em `project_memory_chunks` por similaridade vetorial quando houver embedding
  - sem embedding, retorna `semantic_hits=[]` com aviso (`semantic_warning`), sem erro
- `hybrid`:
  - combina structured + semantic
  - deduplica facts repetidos por chave semantica basica
  - gera resumo curto consolidado

## testes minimos executados
1. Structured por termo conhecido:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/project_brain_query.py \
  --project livecopilot \
  --query "Separacao question_bank knowledge" \
  --mode structured \
  --facts-limit 5 \
  --format text
```
Resultado: retornou fact `Separacao question_bank vs knowledge` e runs relacionados.

2. Hybrid por tema conhecido:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/project_brain_query.py \
  --project livecopilot \
  --query "continuidade" \
  --mode hybrid \
  --facts-limit 6 \
  --memory-limit 5 \
  --format text
```
Resultado: facts e runs relevantes + resumo consolidado.

3. Saida text:
- validada nos testes 1 e 2.

4. Saida json:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/project_brain_query.py \
  --project livecopilot \
  --query "continuidade" \
  --mode hybrid \
  --facts-limit 4 \
  --memory-limit 4 \
  --format json
```
Resultado: payload JSON completo com `related_facts`, `related_runs`, `summary`.

5. Semantic mode com fallback limpo:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/project_brain_query.py \
  --project livecopilot \
  --query "realtime" \
  --mode semantic \
  --format json
```
Resultado: `semantic_hits=[]`, `semantic_warning="nenhum embedding disponivel..."`, sem falha.

## limitacoes
- no estado atual do banco, `project_memory_chunks.embedding` esta vazio; semantic so demonstra fallback.
- resumo ainda e heuristico.
