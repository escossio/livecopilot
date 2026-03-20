# Java Semantic Baseline Report (rerun)

## Timestamp
- `20260319T041654Z`

## Metodologia
- Reexecutado o `semantic_baseline` usando o índice atualizado em `data/semantic_index_experiments/java_pilot/` após o refinement focado.
- Nenhum novo corpus ou embeddings completos; apenas os 4 vetores de refinement já anexados foram considerados.
- Bateria de 18 consultas idêntica à rodada anterior para comparação justa.

## Índice avaliado
- Diretório: `data/semantic_index_experiments/java_pilot/`
- Embeddings: `data/semantic_index_experiments/java_pilot/embeddings.jsonl`
- Metadata: `data/semantic_index_experiments/java_pilot/metadata.json`
- Modelo: `text-embedding-3-large`
- Dimensão: `3072`
- Documentos: `30`
- Chunks: `2648`

## Consultas
1. inheritance in java
2. interface default method
3. generic type erasure
4. checked vs unchecked exception
5. definite assignment
6. switch pattern matching
7. record class
8. sealed class
9. hashmap vs concurrenthashmap
10. java nio path files
11. localdate localdatetime difference
12. executorservice submit callable
13. try with resources
14. stream map filter collect
15. java thread lifecycle
16. volatile vs synchronized
17. virtual threads
18. happens before java

## Comparação com o semantic_baseline anterior
| Consulta | Semântico anterior | Semântico atual | Resultado |
| --- | --- | --- | --- |
| inheritance in java | COERENTE | COERENTE | EMPATE |
| interface default method | COERENTE | COERENTE | EMPATE |
| generic type erasure | COERENTE | COERENTE | EMPATE |
| checked vs unchecked exception | COERENTE | COERENTE | EMPATE |
| definite assignment | COERENTE | COERENTE | EMPATE |
| switch pattern matching | COERENTE | COERENTE | EMPATE |
| record class | PARCIALMENTE_COERENTE | COERENTE | MELHORA |
| sealed class | COERENTE | COERENTE | EMPATE |
| hashmap vs concurrenthashmap | COERENTE | COERENTE | EMPATE |
| java nio path files | COERENTE | COERENTE | EMPATE |
| localdate localdatetime difference | COERENTE | COERENTE | EMPATE |
| executorservice submit callable | COERENTE | COERENTE | EMPATE |
| try with resources | COERENTE | COERENTE | EMPATE |
| stream map filter collect | FALHA | COERENTE | MELHORA |
| java thread lifecycle | PARCIALMENTE_COERENTE | COERENTE | MELHORA |
| volatile vs synchronized | PARCIALMENTE_COERENTE | COERENTE | MELHORA |
| virtual threads | COERENTE | COERENTE | EMPATE |
| happens before java | COERENTE | COERENTE | EMPATE |

## Ganhos após o refinement
- `stream map filter collect`: passou de FALHA para COERENTE com chunk dedicado de Streams.
- `record class`: de PARCIALMENTE_COERENTE para COERENTE com chunk focado em records.
- `java thread lifecycle`: de PARCIALMENTE_COERENTE para COERENTE com chunk de estados de thread.
- `volatile vs synchronized`: de PARCIALMENTE_COERENTE para COERENTE com chunk comparativo direto.

## Decisão
- pronta para closure_decision
- Motivo: Todas as consultas ficaram COERENTE após o refinement focado; a falha de streams foi sanada e os parciais foram resolvidos.

## Resumo numérico
- Lexical: 10 RESPONDIVEL, 7 PARCIALMENTE_RESPONDIVEL, 1 NAO_RESPONDIVEL.
- Semântico (atual): 18 COERENTE, 0 PARCIALMENTE_COERENTE, 0 FALHA.
- Comparação vs semântico anterior: 4 MELHORA, 14 EMPATE, 0 PIORA.
