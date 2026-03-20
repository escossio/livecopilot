# C Semantic Baseline Report (2026-03-16T01:55:08Z)

## 1. Embeddings criados
- Índice isolado em `data/semantic_index_experiments/c_pilot/embeddings.jsonl` contendo 23 registros (cada um com chunk_id, família, título e o embedding de texto).
- Metadata (`metadata.json`) registra 23 chunks com média de 582 palavras, dimensão 3072 e modelo `text-embedding-3-large` (timestamp `2026-03-16T01:55:08.532376+00:00`).

## 2. Bateria executada
1. O que é comportamento definido pela implementação em C?
2. O que é locale em C?
3. Para que serve stdio.h?
4. O que pthread_create faz?
5. O que read faz?
6. O que é <assert.h>?
7. Para que serve assert?
8. O que printf retorna?
9. Quando printf pode falhar?

## 3. Comparação lexical vs semântica
| Pergunta | Lexical (chunk/status) | Semântico (chunk/status) | Observação |
| --- | --- | --- | --- |
| O que é comportamento definido pela implementação em C? | `posix_issue7/posix_issue7-05.txt` (COERENTE) | `wg14/wg14-01.txt` (COERENTE) | Semântico acertou o contexto normativo, enquanto o lexical recaiu num trecho sobre `read()`.| 
| O que é locale em C? | `man7/printf-3.txt` (COERENTE) | `cppreference_c/header.txt` (FALHA) | Nem o chunk lexical nem o semântico explicam locales; esse tema precisa de conteúdo novo.| 
| Para que serve stdio.h? | `posix_issue7/posix_issue7-01.txt` (COERENTE) | `posix_issue7/posix_issue7-01.txt` (COERENTE) | Ambas as abordagens usam o mesmo chunk e fornecem a lista de tipos definidos por `<stdio.h>`.|
| O que pthread_create faz? | `posix_issue7/posix_issue7-03.txt` (COERENTE) | `posix_issue7/posix_issue7-04.txt` (COERENTE) | O semântico selecionou o chunk dedicado à função, enquanto o lexical ficou na definição geral de pthread.| 
| O que read faz? | `posix_issue7/posix_issue7-03.txt` (COERENTE) | `posix_issue7/posix_issue7-05.txt` (COERENTE) | O semântico reaproveitou o chunk certo (`read`), melhor alinhado que o chunk lexical mais genérico.| 
| O que é <assert.h>? | `cppreference_c/cppreference_c-06.txt` (PARCIALMENTE COERENTE) | `cppreference_c/cppreference_c-06.txt` (FALHA) | O chunk atual contém apenas o título `<assert.h>`; precisamos enriquecer esse pedaço com o texto real.| 
| Para que serve assert? | `posix_issue7/posix_issue7-01.txt` (COERENTE) | `cppreference_c/cppreference_c-06.txt` (FALHA) | O lexical acerta por aproximação, mas o semântico retorna o mesmo chunk inútil, indicando dependência do conteúdo disponível.| 
| O que printf retorna? | `man7/printf-3.txt` (COERENTE) | `man7/printf-3.txt` (COERENTE) | Ambos usam a seção RETURN VALUE, então as respostas são coerentes e idênticas.| 
| Quando printf pode falhar? | `posix_issue7/posix_issue7-05.txt` (COERENTE) | `man7/printf-3.txt` (COERENTE) | O semântico foi mais direto ao apontar o retorno negativo em caso de erro; o lexical recorreu ao chunk de `read()`.| 

Dados detalhados em `docs/C_SEMANTIC_BASELINE_RESULTS_20260316T015508Z.json`.

## 4. Resumo por família
- **Lexical**: `posix_issue7` respondeu 6 perguntas como COERENTE, `man7` respondeu 2 COERENTE e `cppreference_c` ficou com 1 PARCIALMENTE COERENTE.
- **Semântico**: `posix_issue7` (3 COERENTE), `man7` (2 COERENTE), `wg14` (1 COERENTE), `cppreference_c` (3 FALHA).

## 5. Observações
- O subset semântico continua limitado para `locale` e `assert`: os chunks disponíveis não trazem explicações completas, e o embedding apenas reforça o texto mínimo.<br>
- As famílias normativas (`wg14`, `posix_issue7`, `man7`) respondem bem às demais perguntas; a baseline pode avançar, mas o corpus precisa de reforço nos cabeçalhos de linguagem e na seção de `<assert.h>`.
