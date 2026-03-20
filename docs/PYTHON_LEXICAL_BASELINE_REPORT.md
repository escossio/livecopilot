# PYTHON Lexical Baseline Report

## Context
- Corpus: 4 chunks derived from official Python docs (language reference, AsyncIO, Packaging, CLI).
- Stage: Post-chunking lexical validation before any embeddings.

## Query Summary
| Query | Top chunk | Top1 relevance | Top3 quality | Notes |
| --- | --- | --- | --- | --- |
| python language reference | `language_reference-chunks.json` | Alta (múltiplos tópicos de sintaxe, modelo de objeto e async) | Alta (derivados: language reference + CLI contextual) | Texto foca no núcleo da linguagem; nenhum ruído detectado |
| python asyncio | `library_asyncio-chunks.json` | Alta (explica event loop, tasks, primitives) | Alta (os outros chunks permanecem específicos a async ou CLI) | Sem lacuna essencial |
| python packaging | `packaging-chunks.json` | Alta (contém pyproject, pip, twine) | Alta (outros chunks são complementares mas não diluem) | Cobertura situacional; nenhum ruído |
| python cli arguments | `cli-chunks.json` | Alta (flags e políticas de inicialização) | Alta (top3 inclui language reference/packaging com menos foco mas ainda técnico) | Isolamento claro, sem duplicação de marketing |

## Observações
- O top1 para cada pergunta é o chunk claramente associado, com frases técnicas suficientes e sem ruído.
- O corpus atual responde as consultas definidas com precisão; top3 permanece relevante por natureza homogênea dos 4 chunks.

## Decision
- **Status**: aprovado para `semantic_embeddings`
- Justificativa: toda a bateria retorna chunks técnicos diretamente ligados às consultas, sem lacunas bloqueantes.
