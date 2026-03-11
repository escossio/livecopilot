# Design Evolution

A evolução do Livecopilot seguiu um padrão pragmático: primeiro provar execução, depois elevar qualidade semântica e controle operacional.

## Arquitetura inicial
A fase inicial foi propositalmente enxuta:
- backend + UI local,
- entrada simulada,
- sugestões básicas,
- módulos separados para facilitar crescimento.

A decisão-chave foi evitar integração pesada cedo demais (áudio real/modelo final) para não bloquear aprendizado do produto.

## Da resposta genérica para resposta contextual
Em rodadas seguintes, o sistema ganhou:
- classificação simples de entrada,
- dicionário técnico inicial,
- estrutura de resposta curta + apoio.

Essa etapa transformou o produto de "painel reativo" para "assistente contextual".

## Entrada da memória de mercado
Com ingestão de vagas, o sistema passou a incorporar sinais de demanda real:
- termos frequentes,
- categorias recorrentes,
- vocabulário de recrutamento.

A resposta deixou de depender só de heurística genérica.

## Entrada da knowledge base documental
A ingestão de documentos técnicos consolidou a segunda memória do sistema:
- parsing,
- chunking,
- busca local,
- integração ao fluxo de sugestão.

Aqui surge a base para explainability e recuperação auditável.

## Separação de camadas (pergunta vs explicação)
Uma virada estrutural foi separar:
- `question_bank` (revelar lacuna),
- `knowledge` (sustentar explicação).

Essa separação reduziu ruído conceitual e permitiu comparação explícita entre "o que se pergunta" e "o que está coberto".

## Gap logic e ação operacional
Com comparador calibrado e gap queue, o sistema passou a operar em ciclo:
1. detectar tema/pergunta,
2. medir cobertura (`covered/partial/missing`),
3. priorizar ingestão,
4. consolidar blocos de ação.

Esse ciclo implementa os princípios-guia do projeto no desenho técnico.

## Maturidade de qualidade: higiene e ranking
Rodadas posteriores focaram em qualidade do acervo e recuperação:
- diagnóstico de tipo real de arquivo,
- detecção de duplicidade,
- score de higiene persistido,
- penalização no ranking e no comparador.

Resultado: documentos problemáticos continuam auditáveis, mas perdem influência.

## Evolução da trilha EPUB
A trilha EPUB recebeu várias melhorias:
- TOC legível,
- limpeza de marcadores internos,
- reflow para reduzir fragmentação,
- chunking estruturado por capítulo/seção,
- metadados estruturais por chunk,
- coerência entre `title`, `chapter_title`, `estimated_topic`.

A evolução reduziu ruído e aumentou explainability.

## Entrada e amadurecimento do realtime
Paralelamente, o módulo realtime evoluiu em fases:
- fase 1: `/realtime/respond`,
- fase 1.5: modos (`interview/study/generic`),
- fase 2: ingest incremental,
- fase 2.5: readiness heurística,
- fase 3: persistência de sessão,
- fase 3.5: TTL + métricas.

Isso consolidou operação contínua com estado e observabilidade.

## Estado de maturidade
O projeto deixou de ser um MVP "que responde" e virou um sistema que:
- consulta contexto,
- mede a própria cobertura,
- detecta lacunas,
- prioriza expansão com critério.

## Classificação de estado histórico
- **Decisão consolidada:** separação `question_bank`/`knowledge`, gap logic, explainability, higiene de acervo, realtime em fases.
- **Hipótese histórica em aberto:** embeddings como camada principal e expansão formal do certification map para múltiplas trilhas.
- **Ideia abandonada:** ingestão direta de chat bruto no banco semântico.
