# Java Lexical Baseline Report

## Timestamp
- `20260319T031057Z`

## Método
- Busca lexical simples sobre os chunks já consolidados em `data/knowledge_chunks/java/`.
- Ranqueamento por correspondência de termos normalizados entre consulta, título, tópico estimado e conteúdo do chunk.
- Sem embeddings, sem expansão de corpus, sem `semantic_baseline`.
- Corpus usado: somente o corpus chunkado oficial da frente `JAVA` já congelado no `corpus_lock`.

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

## Avaliação por consulta

### 1. inheritance in java
- top1: `jep-409-0001` - `JEP 409: Sealed Classes`
- top3/top5: sem variedade útil; só apareceu um chunk relevante.
- relevância do top1: `baixa`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `parcial`
- ruído: sim, o top1 veio por termos genéricos de linguagem, não por cobertura direta de inheritance.

### 2. interface default method
- top1: `java_lang-0001` - `java.lang`
- top3/top5: mistura `java.lang`, `java.io`, `java.util` e `java.util.concurrent`.
- relevância do top1: `baixa`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `média`, porém ruidosa.
- aderência ao escopo Java core: `parcial`
- ruído: alto; os chunks da API docs são amplos demais para isolar default methods.

### 3. generic type erasure
- top1: `java_lang-0001` - `java.lang`
- top3/top5: presença de JEPs de pattern matching e API docs genéricas, sem foco direto em erasure.
- relevância do top1: `baixa`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `média`
- aderência ao escopo Java core: `parcial`
- ruído: alto; o corpus não isola bem generics/erasure em um chunk canônico.

### 4. checked vs unchecked exception
- top1: `java_nio-0001` - `java.nio`
- top3/top5: quase todo o retorno ficou em API docs amplas e sem chunk específico de exceções.
- relevância do top1: `baixa`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `parcial`
- ruído: alto; consulta de exceções cai em chunk de I/O/NIO por coocorrência lexical.

### 5. definite assignment
- top1: sem retorno útil
- top3/top5: sem retorno útil
- relevância do top1: `nula`
- qualidade do top3/top5: `nula`
- diversidade de fontes: `nula`
- aderência ao escopo Java core: `baixa`
- ruído: não aplicável; há lacuna de cobertura lexical explícita.

### 6. switch pattern matching
- top1: `jep-406-0001` - `JEP 406: Pattern Matching for switch (Preview)`
- top3/top5: `jep-441-0001`, `jep-440-0001`, `jep-409-0001`
- relevância do top1: `alta`
- qualidade do top3/top5: `alta`
- diversidade de fontes: `alta`
- aderência ao escopo Java core: `alta`
- ruído: baixo; é o melhor caso do baseline.

### 7. record class
- top1: `java_lang-0001` - `java.lang`
- top3/top5: `jep-440-0001`, `java_io-0001`, `jep-409-0001`, `java_nio-0001`
- relevância do top1: `média`
- qualidade do top3/top5: `média`
- diversidade de fontes: `média`
- aderência ao escopo Java core: `alta`
- ruído: médio; o termo `record` aparece, mas parte do ranking vem de chunks genéricos.

### 8. sealed class
- top1: `jep-409-0001` - `JEP 409: Sealed Classes`
- top3/top5: `java_lang-0001`, `java_io-0001`, `java_nio-0001`, `java_time-0001`
- relevância do top1: `alta`
- qualidade do top3/top5: `média`
- diversidade de fontes: `média`
- aderência ao escopo Java core: `alta`
- ruído: médio; a melhor correspondência é clara, mas o restante é genérico.

### 9. hashmap vs concurrenthashmap
- top1: sem retorno útil
- top3/top5: sem retorno útil
- relevância do top1: `nula`
- qualidade do top3/top5: `nula`
- diversidade de fontes: `nula`
- aderência ao escopo Java core: `baixa`
- ruído: não aplicável; falta chunk lexical forte para as classes específicas.

### 10. java nio path files
- top1: `java_nio-0001` - `java.nio`
- top3/top5: sem diversidade útil além do mesmo pacote.
- relevância do top1: `alta`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `alta`
- ruído: baixo no top1, mas cobertura muito concentrada.

### 11. localdate localdatetime difference
- top1: `java_time-0001` - `java.time`
- top3/top5: sem diversidade útil além do mesmo pacote.
- relevância do top1: `média`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `alta`
- ruído: baixo, mas a consulta não encontra um chunk bem específico de comparação entre `LocalDate` e `LocalDateTime`.

### 12. executorservice submit callable
- top1: `java_util_concurrent-0001` - `java.util.concurrent`
- top3/top5: sem diversidade útil além do mesmo pacote.
- relevância do top1: `alta`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `alta`
- ruído: baixo, porém a resposta lexical continua muito dependente de um pacote amplo.

### 13. try with resources
- top1: `java_lang-0001` - `java.lang`
- top3/top5: sem diversidade útil.
- relevância do top1: `baixa`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `parcial`
- ruído: alto; o chunk não isola a feature com precisão suficiente.

### 14. stream map filter collect
- top1: `java_io-0001` - `java.io`
- top3/top5: `java.util`, `java.util.concurrent`, `jep-444`
- relevância do top1: `baixa`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `média`
- aderência ao escopo Java core: `parcial`
- ruído: alto; a consulta cai em API docs amplas e temas colaterais.

### 15. java thread lifecycle
- top1: `jep-444-0001` - `JEP 444: Virtual Threads`
- top3/top5: `java.lang`, `java.time`, `java.util.concurrent`
- relevância do top1: `média`
- qualidade do top3/top5: `baixa`
- diversidade de fontes: `média`
- aderência ao escopo Java core: `alta`
- ruído: médio; há aproximação temática, mas não um chunk específico de ciclo de vida de threads.

### 16. volatile vs synchronized
- top1: sem retorno útil
- top3/top5: sem retorno útil
- relevância do top1: `nula`
- qualidade do top3/top5: `nula`
- diversidade de fontes: `nula`
- aderência ao escopo Java core: `baixa`
- ruído: não aplicável; há lacuna de cobertura lexical explícita.

### 17. virtual threads
- top1: `jep-444-0001` - `JEP 444: Virtual Threads`
- top3/top5: sem variedade útil além do mesmo JEP.
- relevância do top1: `alta`
- qualidade do top3/top5: `média`
- diversidade de fontes: `baixa`
- aderência ao escopo Java core: `alta`
- ruído: baixo; a consulta está bem ancorada no corpus.

### 18. happens before java
- top1: sem retorno útil
- top3/top5: sem retorno útil
- relevância do top1: `nula`
- qualidade do top3/top5: `nula`
- diversidade de fontes: `nula`
- aderência ao escopo Java core: `baixa`
- ruído: não aplicável; falta chunk lexical forte para o tópico de memória/happens-before.

## Principais achados
- O corpus responde bem a consultas ligadas a mudanças recentes da linguagem e da plataforma, especialmente `switch pattern matching`, `sealed class` e `virtual threads`.
- As consultas mais tradicionais de Java core, como `inheritance`, `definite assignment`, `checked vs unchecked exception`, `try with resources`, `volatile vs synchronized` e `happens-before`, ficaram frágeis ou sem resposta forte.
- A cobertura lexical está concentrada em chunks amplos da API docs e em alguns JEPs, com pouca granulação para conceitos clássicos da linguagem.

## Acertos
- Boa ancoragem lexical em `JEP 406`, `JEP 409`, `JEP 441` e `JEP 444`.
- Boa recuperação para consultas diretamente ligadas a features recentes do ecossistema Java.
- Corpus oficialmente congelado e consistente com o `corpus_lock`.

## Falhas
- Falta chunk específico para conceitos clássicos da linguagem.
- Chunks amplos de `java.lang`, `java.io`, `java.nio`, `java.time` e `java.util.concurrent` geram ruído e ranking fraco.
- Algumas consultas centrais retornaram nada útil, o que impede considerar o baseline lexical estável.

## Lacunas de cobertura
- inheritance
- default methods
- type erasure
- checked vs unchecked exceptions
- definite assignment
- try-with-resources
- thread lifecycle
- volatile vs synchronized
- happens-before
- comparação precisa entre `LocalDate` e `LocalDateTime`
- classes e coleções específicas como `HashMap` e `ConcurrentHashMap`

## Ruídos observados
- O chunk `java.lang` é muito amplo e absorve consultas que deveriam cair em tópicos mais específicos.
- Chunks de API docs de pacote inteiro competem entre si e reduzem precisão no top3/top5.
- Alguns resultados vêm por coocorrência lexical, não por cobertura semântica direta do conceito consultado.

## Decisão
- `precisa refinamento antes de embeddings`
- Motivo: o baseline ainda não cobre com precisão suficiente vários tópicos clássicos do core Java; avançar para embeddings agora preservaria lacunas estruturais e ruídos do recorte atual.
