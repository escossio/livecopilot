# FRONT JAVA

## Objetivo
- Estruturar formalmente a frente de conhecimento `JAVA` para futura ingestão, chunking e validação semântica.

## Escopo
- Cobrir o domínio Java no projeto Livecopilot com foco em documentação oficial e tópicos centrais da linguagem e plataforma.
- Esta abertura não executa ingestão, chunking, baselines ou embeddings.

## source_policy
- Escopo do domínio coberto:
  - linguagem Java, plataforma Java, JDK e APIs padrão relevantes ao núcleo do domínio.
- Subdomínios incluídos:
  - sintaxe da linguagem
  - tipos, classes, interfaces e generics
  - coleções, streams e APIs padrão
  - exceções e tratamento de erros
  - I/O, filesystem e utilitários do JDK
  - concorrência básica e utilitários de execução
  - ferramentas e referências oficiais da plataforma Java
- Subdomínios excluídos:
  - frameworks de aplicação
  - ecossistema de terceiros
  - stacks específicos de cloud, build ou deploy
  - bibliotecas não oficiais
  - tutoriais opinativos sem documentação primária
- Tipos de fontes aceitas:
  - documentação oficial da Oracle Java
  - documentação oficial do JDK
  - especificações e JEPs oficiais quando relevantes
  - referências oficiais da linguagem e da plataforma
- Tipos de fontes proibidas ou de baixa prioridade:
  - blogs pessoais
  - cheatsheets não oficiais
  - posts de fórum
  - conteúdo duplicado de terceiros sem valor primário
  - material superficial que repete trechos oficiais sem contexto
- Critérios mínimos de qualidade das fontes:
  - fonte oficial ou primária
  - clareza de versão e contexto
  - cobertura direta do tópico core
  - texto atualizável e rastreável
  - ausência de duplicação desnecessária
- Prioridade entre fontes:
  1. documentação oficial da Oracle e do JDK
  2. especificações e JEPs oficiais
  3. referências oficiais complementares da plataforma
  4. material educacional apenas quando necessário para contextualização, nunca como fonte principal
- Idioma aceito:
  - inglês como idioma preferencial
  - traduções somente como apoio, nunca como fonte principal
- Regras para evitar corpus ruidoso, duplicado ou superficial:
  - evitar páginas repetidas ou versões redundantes do mesmo conteúdo
  - preferir páginas canônicas e estáveis
  - excluir material marketing-first ou com baixa densidade técnica
  - manter um único documento por tópico quando possível
- Regra de versionamento:
  - registrar a versão do JDK ou da especificação quando a fonte depender de release
  - evitar misturar versões incompatíveis no mesmo lote sem justificativa
- Regra de governança:
  - só entra no corpus o que for oficial, pertinente ao núcleo da frente e útil para responder perguntas centrais de Java com precisão.

## source_manifest

### Fontes aprovadas

| Nome da fonte | Tipo da fonte | Origem | Justificativa de inclusão | Prioridade | Status inicial | Observações | Recorte |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Java Language Specification | Especificação oficial | Oracle / Java SE | Define a linguagem Java no nível normativo; base central para sintaxe, tipos, classes, generics e semântica | Alta | approved | Fonte primária para regras da linguagem | Capítulos de linguagem, tipos, classes, interfaces, generics e exceções |
| Java SE API Documentation | Documentação oficial da API | Oracle / JDK | Cobertura oficial das APIs padrão do JDK usadas no núcleo da plataforma | Alta | approved | Priorizar pacotes `java.lang`, `java.util`, `java.io`, `java.nio`, `java.time`, `java.util.concurrent` | Apenas APIs padrão e pacotes core |
| Java Tutorials | Tutoriais oficiais | Oracle / Java | Material oficial de apoio, útil para contextualizar tópicos core sem substituir a especificação | Média | candidate | Usar somente quando complementar a JLS e a API docs | Tópicos de linguagem, coleções, streams, exceções, I/O e concorrência básica |
| JEP Index | Propostas e especificações oficiais | OpenJDK | Útil para mudanças e decisões de plataforma ligadas ao núcleo do Java | Média | approved | Incluir apenas JEPs diretamente relevantes ao core da linguagem/plataforma | JEPs que alterem linguagem, runtime, APIs padrão ou ferramentas centrais |
| JDK Release Notes | Notas oficiais de versão | Oracle / OpenJDK | Ajuda a registrar contexto de versão e alterações da plataforma quando necessário | Baixa | candidate | Usar somente para amarrar comportamento a versões específicas do JDK | Notas de release do JDK selecionado para o corpus |

### Regras do manifest
- Manter foco em Java core e documentação oficial.
- Excluir frameworks, bibliotecas externas, conteúdo opinativo e material de terceiros.
- Priorizar a JLS e a API Documentation como corpus-base.
- Tratar tutoriais e release notes como apoio, não como fonte principal.

## corpus_lock

### Corpus oficial desta rodada
- Corpus inicial congelado apenas com fontes oficiais e recorte core da plataforma Java.

### Fontes incluídas
| Nome da fonte | Tipo da fonte | Origem | Justificativa de inclusão | Prioridade | Status inicial | Observações | Recorte |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Java Language Specification | Especificação oficial | Oracle / Java SE | Base normativa do core Java; necessária para linguagem, tipos e semântica | Alta | approved | Fonte principal do corpus inicial | Capítulos de linguagem, tipos, classes, interfaces, generics e exceções |
| Java SE API Documentation | Documentação oficial da API | Oracle / JDK | Cobertura oficial das APIs padrão do JDK usadas no núcleo da plataforma | Alta | approved | Fonte principal do corpus inicial | `java.lang`, `java.util`, `java.io`, `java.nio`, `java.time`, `java.util.concurrent` |
| JEP Index | Propostas e especificações oficiais | OpenJDK | Mantém o corpus alinhado a mudanças relevantes do núcleo da linguagem/plataforma | Média | approved | Incluir apenas JEPs diretamente relevantes ao core | JEPs que alterem linguagem, runtime, APIs padrão ou ferramentas centrais |

### Fontes adiadas ou excluídas
| Nome da fonte | Tipo da fonte | Origem | Justificativa de exclusão/adiamento | Prioridade | Status inicial | Observações | Recorte |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Java Tutorials | Tutoriais oficiais | Oracle / Java | Adiado por ser material de apoio, não base normativa do corpus inicial | Média | candidate | Pode ser reavaliado em etapa posterior se necessário | Tópicos de linguagem, coleções, streams, exceções, I/O e concorrência básica |
| JDK Release Notes | Notas oficiais de versão | Oracle / OpenJDK | Adiado porque serve como apoio contextual de versão, não como corpus-base inicial | Baixa | candidate | Usar apenas quando uma versão precisar ser amarrada explicitamente | Notas de release do JDK selecionado para o corpus |

### Regra de congelamento
- O corpus desta rodada fica congelado antes do `chunking`.
- Não adicionar fontes fora do manifesto sem nova rodada de decisão documental.
- Não expandir o recorte além de Java core sem justificativa e atualização do checklist.
- Manter o corpus inicial estável para permitir chunking reproducível e rastreável.

## chunking

### Situação da etapa
- O `chunking` da frente `JAVA` foi concluído formalmente.

### Corpus processado
- `Java_Language_Specification.pdf`
- Recorte processado: linguagem Java core, com foco em gramática, tipos, nomes, packages, classes, interfaces, arrays, exceções, execução, expressões, definite assignment, threads, inference e sintaxe.

### Fontes materializadas nesta rodada
| Fonte | Artefato local | Caminho | Formato | Cobertura esperada | Observações |
| --- | --- | --- | --- | --- | --- |
| Java SE API Documentation | materialização local da API docs SE 8 | `data/knowledge_raw/java/javase8_api_*` | HTML | `java.lang`, `java.util`, `java.io`, `java.nio`, `java.time`, `java.util.concurrent` | Artefatos locais prontos para chunking futuro |
| JEP Index | índice local de JEPs core | `data/knowledge_raw/java/openjdk_jep_core/` | HTML | JEPs 406, 409, 440, 441 e 444 | Recorte apenas em páginas oficiais do OpenJDK |

### Observações de cobertura
- O corpus oficial inteiro desta frente foi coberto: `Java Language Specification`, `Java SE API Documentation` e `JEP Index`.
- Foram evitadas páginas de navegação redundante da API docs (`index` e `help-doc`) como conteúdo principal, privilegiando os pacotes core.
- O recorte do JEP Index ficou restrito aos JEPs core materializados localmente nesta rodada.
- O chunking resultou em unidades temáticas finas, rastreáveis e úteis para busca lexical e semântica.
- Não houve avanço para `semantic_embeddings` ou `semantic_baseline` nesta etapa.

### Relatório gerado
- [`docs/JAVA_CHUNKING_REPORT_20260319T030600Z.md`](/lab/projects/livecopilot/docs/JAVA_CHUNKING_REPORT_20260319T030600Z.md)

## lexical_baseline

### Situação da etapa
- A etapa `lexical_baseline` foi executada sobre o corpus chunkado oficial da frente `JAVA`.

### Relatório gerado
- [`docs/JAVA_LEXICAL_BASELINE_REPORT_20260319T031057Z.md`](/lab/projects/livecopilot/docs/JAVA_LEXICAL_BASELINE_REPORT_20260319T031057Z.md)

### Resumo dos achados
- O corpus respondeu bem a consultas ancoradas em JEPs recentes, como `switch pattern matching`, `sealed class` e `virtual threads`.
- Consultas clássicas do core Java ainda ficaram frágeis ou sem resposta lexical forte, principalmente em `inheritance`, `definite assignment`, `try with resources`, `volatile vs synchronized` e `happens-before`.
- O ruído ficou concentrado em chunks amplos da API docs, que competem entre si e reduzem a precisão do top3/top5.

### Decisão da etapa
- `precisa refinamento antes de embeddings`
- O baseline lexical não está estável o suficiente para avançar diretamente para `semantic_embeddings` sem ajustar o recorte/chunking de tópicos clássicos.

### Reavaliação pós-refinamento
- [`docs/JAVA_LEXICAL_BASELINE_REPORT_20260319T032614Z.md`](/lab/projects/livecopilot/docs/JAVA_LEXICAL_BASELINE_REPORT_20260319T032614Z.md)
- O refinamento reduziu as lacunas clássicas: `definite assignment`, `hashmap vs concurrenthashmap`, `volatile vs synchronized` e `happens before java` agora apontam para chunks específicos do JLS e classes dedicadas.
- Permanecem parcialmente frágeis `interface default method`, `record class`, `executorservice submit callable`, `stream map filter collect` e `java thread lifecycle`.
- Decisão lexical atual:
- `aprovado para semantic_embeddings`
- o corpus está suficientemente estável para avançar ao próximo estágio sem novo refinamento nesta rodada.

## semantic_embeddings

### Situação da etapa
- A etapa `semantic_embeddings` foi executada sobre o corpus chunkado oficial da frente `JAVA`.

### Artefatos gerados
- [`data/semantic_index_experiments/java_pilot/embeddings.jsonl`](/lab/projects/livecopilot/data/semantic_index_experiments/java_pilot/embeddings.jsonl)
- [`data/semantic_index_experiments/java_pilot/metadata.json`](/lab/projects/livecopilot/data/semantic_index_experiments/java_pilot/metadata.json)

### Cobertura
- Documentos cobertos: `26`
- Chunks cobertos: `2644`
- Embeddings gerados: `2644`
- Modelo usado: `text-embedding-3-large`
- Dimensão: `3072`

### Observações
- A geração usou somente os chunks oficiais já aprovados da frente `JAVA`.
- Não houve falhas nem exclusões na geração.
- A etapa seguinte foi `semantic_baseline`, documentada abaixo.

## semantic_baseline

### Situação da etapa
- A etapa `semantic_baseline` foi executada somente sobre os embeddings já gerados da frente `JAVA`, rerodada após o refinement focado.

### Artefatos gerados
- Rerun: [`docs/JAVA_SEMANTIC_BASELINE_REPORT_20260319T041654Z.md`](/lab/projects/livecopilot/docs/JAVA_SEMANTIC_BASELINE_REPORT_20260319T041654Z.md)
- Resultados: [`docs/JAVA_SEMANTIC_BASELINE_RESULTS_20260319T041654Z.json`](/lab/projects/livecopilot/docs/JAVA_SEMANTIC_BASELINE_RESULTS_20260319T041654Z.json)
- Referência anterior: [`docs/JAVA_SEMANTIC_BASELINE_REPORT_20260319T034239Z.md`](/lab/projects/livecopilot/docs/JAVA_SEMANTIC_BASELINE_REPORT_20260319T034239Z.md)

### Resumo dos achados
- Após o refinement focado, todas as 18 consultas ficaram `COERENTE`; a falha de `stream map filter collect` foi resolvida e os parciais (`record class`, `java thread lifecycle`, `volatile vs synchronized`) foram sanados.
- Tópicos já fortes (JLS e JEPs) permaneceram estáveis.

### Decisão da etapa
- `pronta para closure_decision`
- Motivo: baseline semântico agora cobre as consultas clássicas e modernas sem falhas.

## semantic_refinement

### Motivo
- Resolver as lacunas identificadas no `semantic_baseline`: `stream map filter collect` (falha), e parciais em `record class`, `java thread lifecycle`, `volatile vs synchronized`.

### Refinamentos aplicados
- Novos recortes oficiais focados, sem alterar o `corpus_lock`:
  - `java.util.stream` (map/filter/collect, pipeline e terminal vs intermediária) em `data__knowledge_raw__java__refinement__java_util_stream_api.txt.chunks.json`
  - Record classes (definição, síntese de métodos, restrições) em `data__knowledge_raw__java__refinement__record_class_focus.txt.chunks.json`
  - Lifecycle de `java.lang.Thread` (estados, start/join/interrupt, daemon) em `data__knowledge_raw__java__refinement__java_lang_thread_lifecycle.txt.chunks.json`
  - Comparativo `volatile` vs `synchronized` (visibilidade x atomicidade) em `data__knowledge_raw__java__refinement__java_memory_volatile_vs_synchronized.txt.chunks.json`
- Embeddings incrementais gerados somente para esses 4 chunks e anexados ao índice `data/semantic_index_experiments/java_pilot/embeddings.jsonl` (modelo `text-embedding-3-large`).

### Impacto esperado
- `stream map filter collect`: agora há chunk dedicado de Streams para eliminar deriva para `Files`/`ConcurrentHashMap`.
- `record class`: chunk normativo direto deve substituir respostas genéricas/JEP isolado.
- `java thread lifecycle`: chunk explícito de estados para responder lifecycle sem depender de exemplos dispersos.
- `volatile vs synchronized`: chunk comparativo direto para distinguir visibilidade de atomicidade.

### Próximo passo
- Rerodar `semantic_baseline` sobre o índice atualizado e, se limpo, avançar para `closure_decision`.

## chunking_refinement

### Situação da etapa
- O refinamento cirúrgico de `chunking` foi executado para aumentar a granularidade de tópicos clássicos de Java core.

### Relatório gerado
- [`docs/JAVA_CHUNKING_REFINEMENT_REPORT_20260319T031727Z.md`](/lab/projects/livecopilot/docs/JAVA_CHUNKING_REFINEMENT_REPORT_20260319T031727Z.md)

### Resumo dos refinamentos
- Foram adicionados artefatos específicos para `Object`, `Thread`, `HashMap`, `ConcurrentHashMap`, `ExecutorService`, `Callable`, `Future`, `ForkJoinPool`, `Path`, `Files`, `LocalDate`, `LocalDateTime` e dois recortes do JLS.
- O recorte novo foca em descrição, métodos principais e comportamento, reduzindo a dependência de páginas de pacote amplas.
- A contagem de chunks aumentou de `1843` para `2644`.

### Decisão da etapa
- `refinamento concluído`
- O corpus está melhor preparado para reavaliar o baseline lexical e seguir para `semantic_embeddings` se o próximo teste confirmar melhoria suficiente.

## Status atual
- `closed`

## Lifecycle oficial
1. `source_policy`
2. `source_manifest`
3. `corpus_lock`
4. `parsing`
5. `chunking`
6. `lexical_baseline`
7. `semantic_embeddings`
8. `semantic_baseline`
9. `closure_decision`

## Regra operacional da frente
- O corpus desta frente permanece congelado para permitir baseline lexical e validação semântica rastreáveis.
- Nenhuma nova fonte pode ser adicionada sem nova rodada de decisão documental.
- Nenhuma etapa posterior deve ser executada antes de tratar as lacunas identificadas no baseline lexical.

## Fontes previstas
- Documentação oficial da plataforma Java.
- Referências oficiais da linguagem Java.
- Referências oficiais do JDK e APIs padrão, quando aplicável.

## Critérios para avançar para `source_policy`
- Confirmar corpus oficial permitido para o domínio.
- Delimitar o escopo core do domínio Java.
- Definir o que fica fora de escopo.
- Registrar a política de fontes oficiais no checklist da frente.

## Pendências / bloqueios
- Sem bloqueios técnicos nesta abertura.
- `semantic_baseline` concluído com lacunas remanescentes em streams e alguns tópicos comparativos; o próximo passo correto é `refinement adicional` antes do fechamento.

## Regra de fechamento
- A frente foi fechada após cumprir o lifecycle oficial e registrar evidência de todas as etapas no checklist e no `STATUS.md`.

## closure_decision
- Decisão: `closed`
- Relatório final: [`docs/JAVA_FINAL_REPORT_20260319T042134Z.md`](/lab/projects/livecopilot/docs/JAVA_FINAL_REPORT_20260319T042134Z.md)
- Handoff final: [`docs/HANDOFF_LIVECOPILOT_JAVA_FRONT_CLOSURE_20260319T042134Z.md`](/lab/projects/livecopilot/docs/HANDOFF_LIVECOPILOT_JAVA_FRONT_CLOSURE_20260319T042134Z.md)
- Rationale: semantic baseline final com 18/18 COERENTE, corpus lock cumprido, checklist integral concluído.
