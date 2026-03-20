# HANDOFF: C Semantic Baseline (2026-03-16T01:55:08Z)

## Contexto
- Continuação direta do handoff staging de 2026-03-15; a prioridade era desbloquear o sandbox isolado em `data/semantic_index_experiments/c_pilot/` e comparar lexical vs semântico para o subset de C.

## O que foi feito
1. `OPENAI_API_KEY` foi carregado via `codex-supervisor/.env.secrets` apenas para esta rodada, garantindo que o índice global permanece intacto.
2. Gerados 23 embeddings em `data/semantic_index_experiments/c_pilot/embeddings.jsonl` e o resumo em `metadata.json` com stats de 582 palavras em média, dimensão 3072 e modelo `text-embedding-3-large`.
3. A bateria de perguntas C foi executada consultando `scripts/c_semantic_search_test.py` (atualizado para a nova API OpenAI) e o resultado foi cruzado com os dados lexicais existentes para preencher `docs/C_SEMANTIC_BASELINE_RESULTS_20260316T015508Z.json`.
4. Elaborado `docs/C_SEMANTIC_BASELINE_REPORT_20260316T015508Z.md` com a comparação individual e o panorama por família.

## Resultados principais
- As famílias normativas (`wg14`, `posix_issue7`, `man7`) respondem bem às perguntas mais críticas; `wg14` é a única que só aparece no caminho semântico, trazendo contexto de comportamento definido pela implementação.
- As perguntas sobre `<assert.h>` e `locale` ainda não têm chunk explicativo no subset; o clustered embedding simplesmente retorna o nome do cabeçalho e o sinaliza como FALHA.
- O script de busca semântica funciona (ex.: `python3 scripts/c_semantic_search_test.py "O que read faz?"`).

## Próximos passos sugeridos
1. Documentar ou adicionar textos para `locale` e `assert`, atualizar os chunks correspondentes e reexecutar a rotina de geração de embeddings para reforçar a baseline.
2. Validar o handoff final de baseline semântica (nesta pasta) e, se tudo estiver estável, preparar a ingestão semântica/controlada para integrar esse subset ao pipeline sem afetar o índice global.
