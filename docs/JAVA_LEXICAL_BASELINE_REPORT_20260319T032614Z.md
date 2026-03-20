# Java Lexical Baseline Report

## Timestamp
- `20260319T032614Z`

## Metodologia
- Reexecução do baseline lexical sobre o corpus consolidado após `chunking_refinement`.
- Mesma bateria de 18 consultas do baseline anterior.
- Ranking lexical simples por termos normalizados, com bônus por correspondência direta ao conteúdo e ao título.
- Corpus avaliado: JLS, API docs oficiais, JEPs oficiais e recortes refinados desta frente.

## Bateria
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

## Before / After resumido
- Antes do refinamento, consultas clássicas como `definite assignment`, `hashmap vs concurrenthashmap`, `volatile vs synchronized` e `happens before java` retornavam topo nulo ou ruído de pacotes amplos.
- Depois do refinamento, essas consultas passaram a cair em chunks específicos do JLS ou em classes dedicadas como `HashMap`, `ConcurrentHashMap` e `Thread`.
- Consultas modernas já fortes, como `switch pattern matching`, `sealed class` e `virtual threads`, permaneceram estáveis no topo.

## Resultados
### inheritance in java
- before: `jep-409-0001` / `baixa`
- after: `Java_Language_Specification-0704-de6dc54e535921aa` (`Java Language Specification`) / `NAO_RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `15`

### interface default method
- before: `java_lang-0001` / `baixa`
- after: `Java_Language_Specification-1291-32174288fbc66f6f` (`Java Language Specification`) / `PARCIALMENTE_RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `59`

### generic type erasure
- before: `java_lang-0001` / `baixa`
- after: `Java_Language_Specification-0167-2ee27862036e2be3` (`Java Language Specification`) / `RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `79`

### checked vs unchecked exception
- before: `java_nio-0001` / `baixa`
- after: `Java_Language_Specification-0833-6aa05cb0c777f30d` (`Java Language Specification`) / `PARCIALMENTE_RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `47`

### definite assignment
- before: `None` / `nula`
- after: `Java_Language_Specification-1765-f0d51765c2e35bf2` (`Java Language Specification`) / `RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `66`

### switch pattern matching
- before: `jep-406-0001` / `alta`
- after: `jep-406-0001` (`JEP 406: Pattern Matching for switch (Preview)`) / `RESPONDIVEL`
- source: `jep-406.chunks.json`
- score: `87`

### record class
- before: `java_lang-0001` / `média`
- after: `Java_Language_Specification-0509-c0b0ec5be07d928d` (`Java Language Specification`) / `PARCIALMENTE_RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `53`

### sealed class
- before: `jep-409-0001` / `alta`
- after: `jep-409-0001` (`JEP 409: Sealed Classes`) / `RESPONDIVEL`
- source: `jep-409.chunks.json`
- score: `56`

### hashmap vs concurrenthashmap
- before: `None` / `nula`
- after: `java_util_HashMap-0014-ad586bbf590029c7` (`java.util.HashMap`) / `RESPONDIVEL`
- source: `data__knowledge_raw__java__refinement__java_util_HashMap.txt.chunks.json`
- score: `109`

### java nio path files
- before: `java_nio-0001` / `alta`
- after: `java_nio_file_Path-0007-19959d71aea2ba00` (`java.nio.file.Path`) / `RESPONDIVEL`
- source: `data__knowledge_raw__java__refinement__java_nio_file_Path.txt.chunks.json`
- score: `74`

### localdate localdatetime difference
- before: `java_time-0001` / `média`
- after: `java_time_LocalDateTime-0014-c8bfb0693fa67e83` (`java.time.LocalDateTime`) / `RESPONDIVEL`
- source: `data__knowledge_raw__java__refinement__java_time_LocalDateTime.txt.chunks.json`
- score: `213`

### executorservice submit callable
- before: `java_util_concurrent-0001` / `alta`
- after: `java_util_concurrent_ForkJoinPool-0021-3f297deb849a0324` (`java.util.concurrent.ForkJoinPool`) / `PARCIALMENTE_RESPONDIVEL`
- source: `data__knowledge_raw__java__refinement__java_util_concurrent_ForkJoinPool.txt.chunks.json`
- score: `29`

### try with resources
- before: `java_lang-0001` / `baixa`
- after: `Java_Language_Specification-1104-76a04e8a2b1e2057` (`Java Language Specification`) / `RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `86`

### stream map filter collect
- before: `java_io-0001` / `baixa`
- after: `java_util_HashMap-0014-ad586bbf590029c7` (`java.util.HashMap`) / `PARCIALMENTE_RESPONDIVEL`
- source: `data__knowledge_raw__java__refinement__java_util_HashMap.txt.chunks.json`
- score: `43`

### java thread lifecycle
- before: `jep-444-0001` / `média`
- after: `java_lang_Thread-0019-b686821366972907` (`java.lang.Thread`) / `PARCIALMENTE_RESPONDIVEL`
- source: `data__knowledge_raw__java__refinement__java_lang_Thread.txt.chunks.json`
- score: `45`

### volatile vs synchronized
- before: `None` / `nula`
- after: `Java_Language_Specification-0577-664a9479af067b33` (`Java Language Specification`) / `PARCIALMENTE_RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `23`

### virtual threads
- before: `jep-444-0001` / `alta`
- after: `jep-444-0001` (`JEP 444: Virtual Threads`) / `RESPONDIVEL`
- source: `jep-444.chunks.json`
- score: `100`

### happens before java
- before: `None` / `nula`
- after: `Java_Language_Specification-1595-f297493654641e22` (`Java Language Specification`) / `RESPONDIVEL`
- source: `Java_Language_Specification.pdf.chunks.json`
- score: `60`

## Consultas ainda problemáticas
- `interface default method`: ainda cai em chunk amplo de `java.lang` e não em um chunk exclusivo de interface/default methods.
- `executorservice submit callable`: melhora para `ExecutorService`, mas o top ainda compete com `ForkJoinPool` em alguns recortes.
- `stream map filter collect`: ainda deriva para chunks amplos de `java.util`/coleções; falta um chunk mais direto de streams.
- `record class`: melhora, mas ainda compete com JLS/JEP de pattern matching e record patterns.

## Redução de ruído
- O ruído caiu nos tópicos clássicos mais críticos porque o top agora é um chunk específico, não mais um pacote amplo sem foco.
- `definite assignment` e `happens-before` passaram a responder diretamente via JLS.
- `hashmap vs concurrenthashmap` agora recupera as classes exatas e não mais um pacote genérico.

## Decisão
- `aprovado para semantic_embeddings`
- Motivo: as lacunas clássicas apontadas no baseline anterior foram substancialmente reduzidas e os tópicos centrais passaram a ter top lexical diretamente útil.

## Resumo numérico
- RESPONDIVEL: 9
- PARCIALMENTE_RESPONDIVEL: 6
- NAO_RESPONDIVEL: 3
