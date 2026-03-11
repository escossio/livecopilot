# Architecture Decisions

## Classificação canônica usada neste arquivo
- **Decisão consolidada:** adotada e ativa no sistema.
- **Hipótese histórica:** proposta recorrente no histórico, ainda não consolidada como regra arquitetural.
- **Ideia abandonada:** proposta explicitamente rejeitada para proteger qualidade/escopo.

## Decisões consolidadas

## AD-001 — MVP local com modo mock antes de integrações pesadas
- **Contexto:** precisava sair do zero para algo executável rápido.
- **Decisão:** criar base local com FastAPI + UI + entrada simulada.
- **Motivação:** validar fluxo fim-a-fim sem bloqueio por áudio/ASR/modelo final.
- **Consequências:** aceleração inicial; dívida controlada de real-time real.
- **Status:** ativa (base histórica do projeto).

## AD-002 — Separar question_bank de knowledge base
- **Contexto:** perguntas e documentação têm papéis distintos.
- **Decisão:** trilhas/pastas/pipelines separados.
- **Motivação:** evitar usar pergunta como resposta e preservar semântica do sistema.
- **Consequências:** comparador dedicado e diagnóstico mais confiável.
- **Status:** ativa.

## AD-003 — Usar gap detection como núcleo de evolução
- **Contexto:** objetivo deixou de ser só "responder" e passou a ser "aprender onde falta".
- **Decisão:** classificar cobertura (`covered/partial/missing`) e priorizar ingestão.
- **Motivação:** operacionalizar o princípio "saber o que não sabe".
- **Consequências:** criação de `gap queue`, ranking e action plan.
- **Status:** ativa.

## AD-004 — Explainability/debug na recuperação
- **Contexto:** sem inspeção, melhoria de qualidade fica subjetiva.
- **Decisão:** incluir debug (query usada, fontes, contagem, motivos de match).
- **Motivação:** auditoria técnica da recuperação e do ranking.
- **Consequências:** iteração mais segura e menos regressão silenciosa.
- **Status:** ativa.

## AD-005 — Ingestão incremental e reprocessamento por versão
- **Contexto:** corpus cresce continuamente e formatos variam.
- **Decisão:** pipeline incremental com hash/versionamento e reprocessamento quando heurística muda.
- **Motivação:** eficiência, reprodutibilidade e evolução controlada.
- **Consequências:** estado/manifesto persistidos e checkpoints frequentes.
- **Status:** ativa.

## AD-006 — Persistência de sessões realtime + TTL + métricas
- **Contexto:** módulo realtime evoluiu de endpoint simples para operação contínua.
- **Decisão:** persistir sessões, aplicar TTL e expor métricas/sessões operacionais.
- **Motivação:** robustez operacional, inspeção de estado e manutenção de latência.
- **Consequências:** endpoints de sessão/metricas; retenção temporal explícita.
- **Status:** ativa.

## AD-007 — Higiene do acervo como sinal de qualidade
- **Contexto:** arquivos inconsistentes (ex.: HTML salvo como .pdf) contaminavam recuperação.
- **Decisão:** camada `knowledge_hygiene` com flags/score persistidos e penalização de ranking.
- **Motivação:** impedir inflação de evidência por documentos ruins sem excluir auditoria.
- **Consequências:** documentos problemáticos seguem acessíveis, mas com menor impacto.
- **Status:** ativa.

## AD-008 — Chunking estruturado para EPUB
- **Contexto:** EPUBs grandes traziam estrutura útil (capítulos/seções), mas chunking cego gerava ruído.
- **Decisão:** usar TOC/seções para chunking estruturado com fallback para método antigo.
- **Motivação:** aumentar coerência semântica e explainability.
- **Consequências:** chunks com `chapter_title/section_hint`; melhor leitura do suporte.
- **Status:** ativa.

## AD-009 — Recalibração de cobertura por força de evidência
- **Contexto:** comparador estava binário/otimista em parte das rodadas.
- **Decisão:** exigir evidência forte para `covered`, usar `partial` de forma real.
- **Motivação:** honestidade diagnóstica.
- **Consequências:** classificação menos inflada, melhor priorização.
- **Status:** ativa.

## Hipóteses históricas (não consolidadas)

## HH-001 — Busca semântica por embeddings como camada principal de retrieval
- **Contexto:** apareceu como próximo salto após estabilização da busca local.
- **Hipótese:** mover ranking principal para similaridade semântica vetorial.
- **Evidência no histórico:** recorrente como próximo passo, mas sem fechamento canônico nesta reconstrução.
- **Status:** em aberto.

## HH-002 — Expansão formal de certification map para múltiplas trilhas além de Python
- **Contexto:** proposta de ampliar para cloud/devops/redes após maturidade inicial.
- **Hipótese:** usar blueprint de certificações como eixo transversal de cobertura.
- **Evidência no histórico:** discutida como direção de evolução, sem consolidação final nesta rodada.
- **Status:** em aberto.

## Ideias abandonadas

## IA-001 — Ingerir chat bruto diretamente na base semântica
- **Contexto:** chat continha histórico rico, mas com ruído e ambiguidades.
- **Decisão de abandono:** **não** ingerir bruto; extrair documentação canônica antes.
- **Motivação:** reduzir ruído semântico e evitar canonizar rascunho.
- **Consequências:** criação de documentação histórica estruturada em `docs/history/`.
- **Status:** abandonada (com regra operacional ativa de bloqueio).
