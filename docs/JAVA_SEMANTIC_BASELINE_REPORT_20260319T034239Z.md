# Java Semantic Baseline Report

## Timestamp
- `20260319T034239Z`

## Metodologia
- Avaliação semântica executada somente sobre o índice isolado já existente em `data/semantic_index_experiments/java_pilot/`.
- Nenhum chunk foi refeito, nenhuma fonte nova foi aberta e nenhum embedding de corpus foi regenerado nesta rodada.
- As 18 consultas foram projetadas no mesmo espaço vetorial (`text-embedding-3-large`) e comparadas por similaridade cosseno contra os `2644` embeddings já persistidos.
- A referência lexical usada para comparação foi [`docs/JAVA_LEXICAL_BASELINE_REPORT_20260319T032614Z.md`](/lab/projects/livecopilot/docs/JAVA_LEXICAL_BASELINE_REPORT_20260319T032614Z.md).
- O detalhamento por consulta, incluindo top5, diversidade, ruído e aderência, foi registrado em [`docs/JAVA_SEMANTIC_BASELINE_RESULTS_20260319T034239Z.json`](/lab/projects/livecopilot/docs/JAVA_SEMANTIC_BASELINE_RESULTS_20260319T034239Z.json).

## Corpus avaliado
- Diretório do índice: `data/semantic_index_experiments/java_pilot/`
- Embeddings file: `data/semantic_index_experiments/java_pilot/embeddings.jsonl`
- Metadata file: `data/semantic_index_experiments/java_pilot/metadata.json`
- Modelo: `text-embedding-3-large`
- Dimensão: `3072`
- Documentos cobertos: `26`
- Chunks cobertos: `2644`
- Falhas herdadas do índice: `0`

## Consultas usadas
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

## Lexical vs semântico
| Consulta | Lexical top | Semantic top | Resultado |
| --- | --- | --- | --- |
| inheritance in java | `Java_Language_Specification-0704-de6dc54e535921aa` / NAO_RESPONDIVEL | `Java_Language_Specification-0533-6719d7fdd5443c0a` / COERENTE | MELHORA |
| interface default method | `Java_Language_Specification-1291-32174288fbc66f6f` / PARCIALMENTE_RESPONDIVEL | `Java_Language_Specification-0996-4f5db01a3afdabf0` / COERENTE | MELHORA |
| generic type erasure | `Java_Language_Specification-0167-2ee27862036e2be3` / RESPONDIVEL | `Java_Language_Specification-0168-5cb7cb624d49bc12` / COERENTE | EMPATE |
| checked vs unchecked exception | `Java_Language_Specification-0833-6aa05cb0c777f30d` / PARCIALMENTE_RESPONDIVEL | `Java_Language_Specification-0841-fe797843dc40b952` / COERENTE | MELHORA |
| definite assignment | `Java_Language_Specification-1765-f0d51765c2e35bf2` / RESPONDIVEL | `jls_threads_locks-0001-869bc178b120351e` / COERENTE | EMPATE |
| switch pattern matching | `jep-406-0001` / RESPONDIVEL | `jep-406-0001` / COERENTE | EMPATE |
| record class | `Java_Language_Specification-0509-c0b0ec5be07d928d` / PARCIALMENTE_RESPONDIVEL | `jep-440-0001` / PARCIALMENTE_COERENTE | EMPATE |
| sealed class | `jep-409-0001` / RESPONDIVEL | `jep-409-0001` / COERENTE | EMPATE |
| hashmap vs concurrenthashmap | `java_util_HashMap-0014-ad586bbf590029c7` / RESPONDIVEL | `java_util_concurrent_ConcurrentHashMap-0006-bd16d4a0a7202be2` / COERENTE | EMPATE |
| java nio path files | `java_nio_file_Path-0007-19959d71aea2ba00` / RESPONDIVEL | `java_nio_file_Path-0004-087c3f13a6749252` / COERENTE | EMPATE |
| localdate localdatetime difference | `java_time_LocalDateTime-0014-c8bfb0693fa67e83` / RESPONDIVEL | `java_time_LocalDateTime-0002-afc765fb025316b2` / COERENTE | EMPATE |
| executorservice submit callable | `java_util_concurrent_ForkJoinPool-0021-3f297deb849a0324` / PARCIALMENTE_RESPONDIVEL | `java_util_concurrent_ExecutorService-0008-7a5c7ed6b2dded25` / COERENTE | MELHORA |
| try with resources | `Java_Language_Specification-1104-76a04e8a2b1e2057` / RESPONDIVEL | `Java_Language_Specification-1101-71151cb5c8f33680` / COERENTE | EMPATE |
| stream map filter collect | `java_util_HashMap-0014-ad586bbf590029c7` / PARCIALMENTE_RESPONDIVEL | `java_nio_file_Files-0029-5977c16d090eb2a1` / FALHA | PIORA |
| java thread lifecycle | `java_lang_Thread-0019-b686821366972907` / PARCIALMENTE_RESPONDIVEL | `java_lang_Thread-0002-1c8594d6f49d7ca8` / PARCIALMENTE_COERENTE | EMPATE |
| volatile vs synchronized | `Java_Language_Specification-0577-664a9479af067b33` / PARCIALMENTE_RESPONDIVEL | `Java_Language_Specification-0547-9074dd2020b38ef7` / PARCIALMENTE_COERENTE | EMPATE |
| virtual threads | `jep-444-0001` / RESPONDIVEL | `jep-444-0001` / COERENTE | EMPATE |
| happens before java | `Java_Language_Specification-1595-f297493654641e22` / RESPONDIVEL | `Java_Language_Specification-1595-f297493654641e22` / COERENTE | EMPATE |

## Achados principais
- O semântico melhorou claramente consultas clássicas antes frágeis, em especial `inheritance in java`, `interface default method`, `checked vs unchecked exception` e `executorservice submit callable`.
- `definite assignment` e `happens before java` permanecem fortes semanticamente sobre o material refinado do JLS, mesmo com alguma baixa diversidade de fonte por serem tópicos normativos.
- O ganho semântico foi mais evidente quando o refinamento criou chunks de classe ou recortes de especificação mais focados; o índice parou de depender tanto de pacotes amplos.
- A principal falha restante é `stream map filter collect`, que ainda deriva para `Files` e `ConcurrentHashMap` por ausência de chunks dedicados a `java.util.stream` no corpus atual.

## Comparação lexical vs semântico
- MELHORA: `4`
- EMPATE: `13`
- PIORA: `1`
- Consultas com melhora semântica: `inheritance in java, interface default method, checked vs unchecked exception, executorservice submit callable`
- Consultas equivalentes ao lexical: `generic type erasure, definite assignment, switch pattern matching, record class, sealed class, hashmap vs concurrenthashmap, java nio path files, localdate localdatetime difference, try with resources, java thread lifecycle, volatile vs synchronized, virtual threads, happens before java`
- Consultas em que o semântico piorou: `stream map filter collect`

## Lacunas remanescentes
- `stream map filter collect`: falha semântica por ausência de cobertura específica de streams.
- `record class`: ainda aproxima por `JEP 440` e trechos genéricos do JLS, sem cair num chunk dedicado de records.
- `java thread lifecycle`: a recuperação é útil, mas não chega num trecho explicitamente orientado a lifecycle/states.
- `volatile vs synchronized`: o semântico encontra os mecanismos corretos, mas não um trecho comparativo direto entre ambos.

## Decisão
- `semantic baseline executado`
- `precisa refinamento adicional antes do fechamento`
- Motivo: A recuperação semântica melhorou materialmente os tópicos clássicos, mas ainda há uma falha clara em `stream map filter collect` e lacunas parciais em `record class`, `java thread lifecycle` e `volatile vs synchronized`.

## Resumo numérico
- Lexical: 10 RESPONDIVEL, 7 PARCIALMENTE_RESPONDIVEL, 1 NAO_RESPONDIVEL.
- Semântico: 14 COERENTE, 3 PARCIALMENTE_COERENTE, 1 FALHA.
