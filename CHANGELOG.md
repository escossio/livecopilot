# Changelog

## [Unreleased]

### CKAD Parsing Baseline Checkpoint

- A frente de granularidade dos 9 modulos CKAD foi encerrada como baseline estavel.
- Todos os modulos permaneceram `exercise` em `devops`, sem falso positivo de `python`.
- Melhor caso observado: `i.crd`.
- Pior caso remanescente: `c.pod_design`.
- Veredito atual da heuristica: `aceitavel com ressalvas`.
- Decisao operacional: nao abrir novo patch de parsing agora; reabrir apenas se houver impacto real em consumo ou busca.

### Question Bank Action Topic Contract

- Documentado explicitamente que `data/question_bank_items/*.items.json` persistem apenas metadados-base por item.
- `action_topic` nao faz parte do schema persistido desses artefatos.
- O campo nasce apenas no relatorio de acao, derivado em tempo de execucao a partir de `inferred_subtheme`, `inferred_domain`, `inferred_tags` e `prompt`.
- A ausencia de `action_topic` em `CKA_Exercises_Practice.md.items.json` e `Kubernetes_HandsOn_Labs.md.items.json` nao e bug; os sinais Kubernetes corretos ja estao persistidos via `inferred_tags`, e o report agrega `action_topic="kubernetes"` sem exigir persistencia adicional.

### Docker Curation Checkpoint

- A trilha Docker foi revisada com leitura real de conteudo dos dois EPUBs locais pendentes em `knowledge`.
- `docker-for-developers-local-data-source-candidates-files-knowledge-docker-for-de` foi aprovado manualmente com cautela, mantido como `medium_trust` e agora esta pronto para promocao, sem ter sido promovido nesta etapa.
- `docker-zero-to-production-hero-local-data-source-candidates-files-knowledge-dock` permaneceu pendente, sem aprovacao manual.
- Estado agregado atual:
  - `candidate_summary.promoted_count = 5`
  - `promotion_readiness.ready = 1`
  - `promotion_readiness.not_ready = 30`

### Editorial Duplicate Policy Checkpoint

- Variantes editoriais da mesma obra com o mesmo `identifier` passaram a ser tratadas documentalmente como duplicata redundante.
- A regra padrao formalizada e manter um unico exemplar por `identifier`.
- Metadata mais limpa, titulo mais bonito ou descricao melhor nao justificam coexistencia por si so.
- No maximo isso justifica futura normalizacao documental, nao um novo fluxo curatorial.
- O caso piloto validado foi `Designing Distributed Systems`, classificado como duplicata redundante sem ganho tecnico real.

### Added

- Camada de ingestao por fontes curadas, separada do nucleo de `knowledge` e `question_bank`, com:
  - `data/source_indexes/`
  - `data/source_candidates/`
  - `data/raw_review/`
  - `data/question_bank_low_trust/`
  - `data/coverage_inputs/`
- Politica curta de confianca em `INGESTION_POLICY.md`.
- CLI `app.services.curated_sources` + wrapper `scripts/curated_sources.sh` para:
  - bootstrap do piloto
  - registro de candidatos
  - atualizacao de status
  - relatorio da camada curada
- Seed inicial do piloto com indices:
  - `Awesome Python`
  - `Awesome React`
  - `Awesome FastAPI`
  - `Awesome Kubernetes`

- Estrutura separada para **question bank**, distinta da base de documentação:
  - `data/question_bank_raw/`
  - `data/question_bank_parsed/`
  - `data/question_bank_items/`
- Pipeline próprio de ingestão de questionários, separado da trilha de knowledge.
- Extração estruturada de itens de pergunta com suporte inicial a materiais em `pdf`, `md` e formatos correlatos.
- Camada de comparação **question_bank vs knowledge** por:
  - `inferred_tags`
  - `inferred_domain`
  - `inferred_subtheme`
- Endpoint:
  - `GET /api/question-bank/coverage`
- Script:
  - `scripts/question_bank_coverage.sh`
- Relatório de cobertura com estados:
  - `covered`
  - `partial`
  - `missing`
- Camada prática de ação para transformar cobertura em prioridade de ingestão:
  - `missing_actions`
  - `partial_actions`
  - `covered_actions`
  - `merged_ingestion_ranking`
- Endpoint:
  - `GET /api/question-bank/action-plan`
- Script:
  - `scripts/question_bank_action.sh`
- Nova camada de consolidação semântica do plano de ação:
  - `consolidated_ingestion_blocks`
- Blocos consolidados com:
  - `action_block`
  - `canonical_topic`
  - `related_topics`
  - `total_priority`
  - `sources_contributing`
  - `suggested_queries`

### Changed

- `question_bank_coverage` passou a respeitar `is_strong_evidence=false` quando o manifesto documental trouxer esse metadado, rebaixando esse material para descoberta/apoio fraco em vez de evidencia forte.
- O parser do **question bank** recebeu higienização mínima para reduzir ruído de PDFs e dumps:
  - descarte de branding
  - descarte de front matter
  - descarte de URLs
  - descarte de texto editorial óbvio
  - exigência de sinal mais forte de item avaliativo
- A extração do `question_bank` foi reduzida de **437** itens brutos para **64** itens úteis após limpeza.
- A inferência de metadata do `question_bank` foi reforçada com:
  - heurísticas por prompt Python
  - contexto do arquivo de origem (`PCEP`, `PCAP`, `PCPP1`)
  - apoio do `python_cert_map`
- O comparador `question_bank vs knowledge` deixou de ser binário e passou a usar **força de evidência**.
- `covered` agora exige evidência forte:
  - subtema específico
  - múltiplas tags coerentes
  - ou suporte documental forte
- `partial` passou a representar cobertura genérica/contextual.
- O relatório de cobertura passou a expor:
  - `coverage_score`
  - `evidence_signals`
  - `reason`
- O plano de ação foi consolidado semanticamente para agrupar tópicos parecidos em frentes mais executáveis.

### Fixed

- Redução de falsos `missing` causados por falta de metadata em perguntas Python genéricas.
- Redução de falsos `covered` causados por inferência excessivamente contextual baseada apenas em trilha/certificação.
- Melhor separação entre:
  - materiais que **revelam lacunas** (question bank)
  - materiais que **preenchem lacunas** (knowledge)

### Improved

- A gap analysis agora é mais honesta:
  - antes: `covered=64`, `partial=0`, `missing=0`
  - depois: `covered=42`, `partial=22`, `missing=0`
- O plano de ingestão passou de lista repetitiva para blocos consolidados.

Exemplos de blocos atuais:
- **python modules and packages**
- **python backend web**

### Curadoria Checkpoint

- Camada de curadoria estabilizada nesta fase com distinção explícita entre `source_origin=web` e `source_origin=local_file`.
- Candidatos locais podem carregar `artifact_path`.
- `report` entrega visão geral da curadoria e `validate-candidates` entrega auditoria rápida de consistência.
- O fallback conservador de `by_origin` para candidatos sem `source_origin` está documentado e coberto por teste, sem ocultar `candidate_consistency.missing_source_origin`.
- Esta frente foi estabilizada sem tocar no núcleo de ingestão.
- Estado atual:
  - `candidate_summary.count = 26`
  - `candidate_summary.promoted_count = 0`

### Curadoria CLI Checkpoint

- A CLI de curadoria agora suporta criação de candidatos por `--url` e por `--artifact-path`.
- Candidatos locais nascem com `artifact_path`, `source_origin=local_file` e `source_url=local://<artifact_path>`.
- O contrato do parser foi fechado e está coberto por teste:
  - rejeição de `--url` + `--artifact-path`
  - rejeição de chamada sem nenhum dos dois
- Esta frente foi estabilizada sem tocar no núcleo de ingestão.
- Estado atual:
  - `candidate_summary.count = 26`
  - `candidate_summary.promoted_count = 0`

### Curadoria Operacional Checkpoint

- A CLI de inspeção da curadoria foi expandida e estabilizada.
- `list-candidates` agora cobre filtros operacionais, JSON Lines, seleção de campos, wrapper compacto e inspeção de `artifact_path` com existência real do arquivo.
- `candidate-stats` fornece resumo operacional curto e `validate-candidates` cobre auditoria rápida de consistência.
- Esta frente foi estabilizada sem tocar no núcleo de ingestão.
- Estado atual:
  - `candidate_summary.promoted_count = 0`
  - suíte local com `37` testes passando

### Curadoria Export Checkpoint

- A curadoria agora tem fluxo operacional mínimo de exportação via CLI + redirecionamento.
- `list-candidates` pode ser usado com filtros, `--json-lines` e `--field` para gerar JSONL operacional.
- Esse fluxo foi formalizado no `README.md` e validado com exportação real para `tmp/local_candidates.jsonl`.
- Esta frente foi estabilizada sem tocar no núcleo de ingestão.
- Estado atual:
  - `candidate_summary.promoted_count = 0`

### Curadoria Audit Summary Checkpoint

- A interface operacional de auditoria da curadoria foi expandida e estabilizada.
- `candidate-audit-summary` agora oferece snapshot único de warnings, categorias ativas opcionais, contagens por categoria opcionais e ordenação opcional de `category_counts`.
- Esta frente foi estabilizada sem tocar no núcleo de ingestão.
- Estado atual:
  - `total_warning_count = 0`
  - `is_clean = true`
  - `candidate_summary.promoted_count = 0`
  - suíte local com `64` testes passando

### Curadoria Promotion Checkpoint

- A primeira versão de promoção manual controlada foi estabilizada.
- O fluxo operacional desta frente ficou: `check-promotion` -> revisão humana -> `promote-candidate --confirm`.
- `check-promotion` agora oferece modo completo e `--compact`.
- O preflight explicita elegibilidade, destino previsto, necessidade real de cópia, equivalência de destino, conflito e motivo curto de conflito.
- Esta frente foi estabilizada sem automação e sem lote.
- Estado atual:
  - `candidate_summary.promoted_count = 0`
  - suíte local com `79` testes passando

### Curadoria Review Checkpoint

- A interface de revisão humana assistida foi estabilizada.
- `review-candidate` agora oferece modo completo e `--compact`.
- A revisão reúne contexto de identidade, artefato, preflight e flags resumidas de auditoria.
- O fluxo humano antes da promoção ficou claro: `check-promotion` -> `review-candidate` -> `promote-candidate --confirm`.
- Esta frente foi estabilizada sem automação e sem lote.
- Estado atual:
  - `candidate_summary.promoted_count = 0`
  - suíte local com `86` testes passando

### Curadoria Review Promotion Checkpoint

- A frente integrada de revisão humana, preflight e promoção manual foi estabilizada.
- O fluxo operacional desta frente ficou: `record-review-decision` -> `check-promotion` -> `review-candidate` -> `promote-candidate --confirm`.
- A promoção manual agora exige `review_decision=approved`.
- O sistema já expõe histórico leve de promoção e ferramentas de inspeção/listagem operacional.
- Esta frente foi estabilizada sem automação e sem lote.
- Estado atual:
  - `candidate_summary.promoted_count = 0`
  - suíte local com `125` testes passando

### Curadoria Promotion Readiness Checkpoint

- A visao operacional de prontidao para promocao foi estabilizada.
- `candidate-stats` agora resume quantos candidatos estao prontos ou nao para promocao manual.
- `list-candidates --promotion-ready true|false` agora lista quais candidatos estao prontos ou nao.
- Ambos reutilizam a mesma regra real do preflight.
- Esta frente foi estabilizada sem automacao e sem lote.
- Estado atual:
  - `ready = 1`
  - `not_ready = 25`
  - `candidate_summary.promoted_count = 0`
  - suíte local com `131` testes passando

### Current Outcome

O projeto agora possui:

- memória de mercado
- memória documental
- question bank separado
- comparação entre perguntas e documentação
- cobertura calibrada por evidência
- plano de ação por prioridade
- consolidação temática em blocos acionáveis

Em termos práticos, o livecopilot deixou de ser apenas um protótipo que responde e passou a funcionar como um sistema que:

1. detecta lacunas,
2. mede cobertura,
3. prioriza ingestão,
4. organiza o próximo aprendizado.
