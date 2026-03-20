# PYTHON Semantic Baseline Report

## Context
- Índice: `data/semantic_index_experiments/python/` (text-embedding-3-large, dim 3072, 4 embeddings).
- Corpus: queries sobre language reference, asyncio, packaging e CLI arguments.

## Query breakdown
| Query | Top1 chunk | Top3 quality | Ruído | Observações |
| --- | --- | --- | --- | --- |
| python language reference | `language_reference-chunks.json` | Alta | Nenhum | O texto aborda sintaxe e modelo de objeto, combinando com CLI e packaging sem misturar domínios. |
| python asyncio | `library_asyncio-chunks.json` | Alta | Nenhum | O chunk descreve event loop, tasks e locking, alinhado ao escopo. |
| python packaging | `packaging-chunks.json` | Alta | Nenhum | Padrão de pyproject/pip/twine, sem ruídos externos. |
| python cli arguments | `cli-chunks.json` | Alta | Nenhum | Flags, startup e ambiente CLI cobertos em profundidade. |

## Decisão
- Baseline aprovado para semantic_embeddings; o ranking semântico recupera os chunks esperados, sem ruído de outros domínios e com top1 de alta relevância.
