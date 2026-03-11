# livecopilot

Copiloto de comunicacao em tempo real para conversas ao vivo. Esta e a primeira versao funcional do MVP local, com ingestao simulada, transcricao mock e geracao de sugestoes basicas.

## Como rodar

1) Crie um ambiente virtual e instale dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) (Opcional) Copie `.env.example` para `.env` e ajuste os valores.

3) Rode o servidor:

```bash
scripts/start.sh
```

Acesse `http://localhost:8000`.

## Ingestao local de conhecimento

Estrutura usada:

- `data/knowledge_raw/`
- `data/knowledge_parsed/`
- `data/knowledge_chunks/`
- `data/knowledge_index/`

Coloque arquivos locais em `data/knowledge_raw/` e rode:

```bash
scripts/ingest_knowledge.sh
```

Opcoes uteis:

```bash
scripts/ingest_knowledge.sh --chunk-size 1200 --overlap 180
```

Formatos suportados nesta etapa:

- `.txt`
- `.md`
- `.pdf`
- `.docx`
- `.html` / `.htm`

Saidas geradas:

- documentos parseados em `data/knowledge_parsed/`
- chunks em `data/knowledge_chunks/`
- manifesto incremental em `data/knowledge_index/knowledge_manifest.json`
- estado de reprocessamento em `data/knowledge_index/knowledge_state.json`

## Ingestao separada de questionarios

Estrutura usada:

- `data/question_bank_raw/`
- `data/question_bank_parsed/`
- `data/question_bank_items/`

Coloque materiais de perguntas e avaliacao em `data/question_bank_raw/` e rode:

```bash
scripts/ingest_question_bank.sh
```

Formatos suportados nesta etapa:

- `.txt`
- `.md`
- `.pdf`
- `.docx`
- `.html` / `.htm`

Saidas geradas:

- documentos parseados em `data/question_bank_parsed/`
- itens estruturados em `data/question_bank_items/`
- manifesto incremental em `data/question_bank_items/question_bank_manifest.json`
- estado de reprocessamento em `data/question_bank_items/question_bank_state.json`

Heuristicas iniciais da trilha `question_bank`:

- linhas terminadas com `?`
- itens numerados como `1.` ou `2)`
- alternativas como `A)`, `B)`, `C)`, `D)`
- aproveitamento de `gabarito`, `resposta`, `hint` e similares como `answer_hint`

Consulta inicial separada da knowledge base:

```bash
curl "http://localhost:8000/api/question-bank/search?q=iam+policy&limit=5"
python3 -m app.services.question_bank_search "iam policy" --limit 5 --pretty
```

Diagnostico inicial de cobertura `question_bank` vs `knowledge`:

```bash
scripts/question_bank_coverage.sh --top 10 --pretty
curl "http://localhost:8000/api/question-bank/coverage?top=10"
```

Plano de acao de ingestao baseado em `missing` e `partial`:

```bash
scripts/question_bank_action.sh --top 10 --pretty
curl "http://localhost:8000/api/question-bank/action-plan?top=10"
```

O plano inclui:

- `merged_ingestion_ranking` com os itens individuais
- `consolidated_ingestion_blocks` com frentes de ingestao deduplicadas
- `suggested_queries` prontas para buscar documentacao nova
- `search_queries`, `source_hints` e `priority_order` por bloco consolidado
- `documentation_search_shortlist` com relatorio pratico para garimpo manual de documentacao

Contrato atual do `question_bank`:

- `data/question_bank_items/*.items.json` persistem apenas metadados-base por item, como `inferred_tags`, `inferred_domain`, `inferred_subtheme`, `difficulty_hint` e payload estrutural da pergunta.
- `action_topic` nao e persistido nesses artefatos.
- `action_topic` e derivado apenas na etapa de action report, em tempo de relatorio, a partir de `inferred_subtheme`, `inferred_domain`, `inferred_tags` e `prompt`.
- Portanto, a ausencia de `action_topic` nos `.items.json` nao e bug; e o contrato atual do pipeline.
- Validacao recente: `CKA_Exercises_Practice.md.items.json` e `Kubernetes_HandsOn_Labs.md.items.json` mantem sinais corretos de Kubernetes via `inferred_tags`, e o action report agrega `action_topic="kubernetes"` sem precisar persistir esse campo por item.

Checkpoint curto da granularidade CKAD:

- A granularidade dos 9 modulos CKAD foi estabilizada como baseline operacional.
- Todos seguem `item_type=exercise`, `inferred_domain=devops` e sem falso positivo de `python`.
- Melhor modulo observado: `i.crd`.
- Pior caso remanescente: `c.pod_design`.
- Veredito atual: `aceitavel com ressalvas`.
- Decisao operacional: parar aqui e so reabrir a frente se houver impacto real em consumo ou busca.

## Camada de ingestao por fontes curadas

Nova camada de staging para descoberta e triagem, sem misturar indices curados com conhecimento final:

- `data/source_indexes/`
- `data/source_candidates/`
- `data/raw_review/`
- `data/question_bank_low_trust/`
- `data/coverage_inputs/`

Mapeamento das camadas finais existentes:

- `knowledge` -> `data/knowledge_raw/`
- `question_bank` -> `data/question_bank_raw/`

Regra principal:

- indices curados e listas de links servem para descoberta
- eles nao contam como evidencia forte direta
- so conteudo promovido deve seguir para `knowledge`, `question_bank` ou `coverage_inputs`

Politica curta:

- `high_trust`: pode virar evidencia forte apos promocao
- `medium_trust`: entra com cautela; nao nasce como evidencia forte
- `curated_index`: descoberta apenas
- `low_trust` / `gray_source`: vao para revisao

Bootstrap do piloto com Awesome repos:

```bash
scripts/curated_sources.sh bootstrap-pilot
scripts/curated_sources.sh report
scripts/curated_sources.sh candidate-stats
scripts/curated_sources.sh validate-candidates
scripts/curated_sources.sh list-candidates --origin local_file
```

- `report`: visao geral da camada de curadoria.
- `candidate-stats`: resumo operacional curto com contagens por origem, destino e estado de artefatos.
- `validate-candidates`: auditoria rapida de consistencia de proveniencia; alerta, mas nao bloqueia o fluxo.
- `audit-metadata`: auditoria leve da qualidade dos metadados da curadoria antes de qualquer frente futura de promocao.
- `audit-semantic`: auditoria leve de combinacoes suspeitas entre `source_origin`, `source_kind`, `trust_level` e `destination`.
- `audit-operational`: auditoria leve de cobertura e coerencia operacional de `discovered_from`, `parser_hint`, `artifact_path` e `source_url`.
- `candidate-audit-summary`: snapshot unico e curto do estado das auditorias da curadoria.
- `candidate-audit-summary --show-nonzero-categories`: mostra so os nomes das categorias com warning, sem detalhar candidatos.
- `candidate-audit-summary --show-category-counts`: mostra nomes + contagens das categorias com warning, sem detalhar candidatos.
- `candidate-audit-summary --show-category-counts --sort-category-counts`: ordena `category_counts` por contagem decrescente e desempate alfabetico.
- `check-promotion`: preflight somente leitura da promocao; mostra elegibilidade real, destino previsto, se haveria copia fisica, se o destino ja bate com o artefato atual, se ha conflito de conteudo via `has_conflict`, o motivo curto em `conflict_reason` e o estado principal em `eligibility_code`.
- `check-promotion --compact`: visualizacao enxuta para uso operacional; reduz o payload, nao muda a logica do preflight e agora tambem mostra `review_decision`/`review_decided_at` quando existirem.
- `review-candidate`: revisao humana assistida antes da promocao; agrega identidade, artefato, preflight, flags curtas de auditoria e resumo do historico de promocao quando existir, sem alterar nada.
- `review-candidate --compact`: visualizacao enxuta para revisao rapida no shell; reduz o payload, nao muda a logica da revisao e tambem expõe `eligibility_code`, `review_decision` e `review_decided_at` quando existirem.
- `show-promotion-log --candidate-id ...`: exibe o historico completo de promocao do candidato, sem alterar nada.
- `show-promotion-log --latest-only`: mostra so o ultimo evento de promocao, util para inspecao rapida.
- `show-promotion-log --compact`: visualizacao enxuta do historico; mostra contagem e ultimo evento quando existir.
- `inspect-target-match`: inspecao somente leitura para casos em que o alvo ja existe no destino; ajuda a identificar legado materializado sem historico formal.
- `reconcile-target-match`: comando manual de reconciliacao de legado para casos ja materializados no destino; nao copia arquivo, nao move artefato e so normaliza o estado curatorial no manifesto.
- `record-review-decision`: registra explicitamente a decisao humana (`approved`, `rejected` ou `needs_revision`) no manifesto; nao promove automaticamente.
- `reclassify-destination`: reclassifica manualmente o `destination` de um candidato dentro dos destinos validos do modelo; e uma acao de curadoria, nao promove nada e nao move arquivo.
- `promote-candidate`: primeira versao de promocao manual, explicita e conservadora; promove um candidato por vez, exige `--confirm`, exige `review_decision=approved` e hoje so aceita `local_file` com `destination=knowledge|question_bank`.
- `list-candidates`: inspecao operacional filtravel por origem e destino.
- `list-candidates` agora tambem aceita `--review-decision approved|rejected|needs_revision|none` para acompanhar decisoes humanas sem promover nada.
- `list-candidates` agora tambem aceita `--has-promotion-history true|false` para filtrar candidatos com ou sem historico de promocao no manifesto.
- `list-candidates` agora tambem aceita `--promotion-ready true|false` para filtrar candidatos aptos ou nao a promocao manual usando a regra real do preflight; isso nao promove nada.
- `list-candidates` agora tambem aceita `--eligibility-code <codigo>` para filtrar candidatos pelo motivo principal calculado pelo mesmo preflight real, incluindo `eligible`.
- `list-candidates` tambem aceita `--query` para localizar candidatos por `title` ou `candidate_id`.
- `list-candidates` tambem aceita `--has-artifact-path` para inspecao rapida de candidatos com artefato local anexado.
- `list-candidates` tambem aceita `--artifact-exists present|missing` para auditoria operacional de caminhos validos ou quebrados.
- `list-candidates` tambem aceita `--json-lines` para piping operacional no shell.
- `list-candidates` tambem aceita `--field` repetivel para reduzir o payload por item em uso shell, incluindo `review_decision` e `review_decided_at` para inspecao rapida do estado humano atual.
- `list-candidates` tambem aceita `--compact` para reduzir o wrapper do modo padrao em leitura humana rapida.
- use `report` para leitura geral da curadoria e `validate-candidates` quando a intencao for checar warnings sem depender do relatorio completo.
- use `list-candidates` quando a intencao for inspecionar candidatos concretos sem despejar o manifesto inteiro.

Checkpoint atual curto da trilha Docker:

- `docker-for-developers-local-data-source-candidates-files-knowledge-docker-for-de` foi aprovado com cautela e esta `promotion_ready=true`, mas ainda nao foi promovido; continua `medium_trust` e deve ser tratado como fonte util, nao premium.
- `docker-zero-to-production-hero-local-data-source-candidates-files-knowledge-dock` segue pendente apos revisao real de conteudo.
- Estado agregado atual:
  - `candidate_summary.promoted_count = 5`
  - `promotion_readiness.ready = 1`
  - `promotion_readiness.not_ready = 30`

Regra curta de duplicata editorial:

- variantes editoriais da mesma obra com o mesmo `identifier` devem ser tratadas como duplicata redundante
- a regra padrao e manter um unico exemplar por `identifier`
- metadata mais limpa, titulo mais bonito ou descricao melhor nao justificam coexistencia por si so
- no maximo isso justifica futura normalizacao documental, nao um novo fluxo curatorial
- o caso piloto validado foi `Designing Distributed Systems`

```bash
python3 -m app.services.curated_sources report
python3 -m app.services.curated_sources candidate-stats
python3 -m app.services.curated_sources validate-candidates
python3 -m app.services.curated_sources audit-metadata
python3 -m app.services.curated_sources audit-semantic
python3 -m app.services.curated_sources audit-operational
python3 -m app.services.curated_sources candidate-audit-summary
python3 -m app.services.curated_sources candidate-audit-summary --show-nonzero-categories
python3 -m app.services.curated_sources candidate-audit-summary --show-category-counts
python3 -m app.services.curated_sources candidate-audit-summary --show-category-counts --sort-category-counts
python3 -m app.services.curated_sources check-promotion --candidate-id local-question-bank
python3 -m app.services.curated_sources check-promotion --candidate-id local-question-bank --compact
python3 -m app.services.curated_sources review-candidate --candidate-id local-question-bank
python3 -m app.services.curated_sources review-candidate --candidate-id local-question-bank --compact
python3 -m app.services.curated_sources show-promotion-log --candidate-id local-question-bank
python3 -m app.services.curated_sources show-promotion-log --candidate-id local-question-bank --latest-only
python3 -m app.services.curated_sources show-promotion-log --candidate-id local-question-bank --compact
python3 -m app.services.curated_sources inspect-target-match --candidate-id local-question-bank
python3 -m app.services.curated_sources reconcile-target-match --candidate-id local-question-bank
python3 -m app.services.curated_sources record-review-decision --candidate-id local-question-bank --decision approved --notes "manual review ok"
python3 -m app.services.curated_sources reclassify-destination --candidate-id local-question-bank --destination knowledge --reason "manual reclassification after triage"
python3 -m app.services.curated_sources candidate-stats
# se `target_already_matches=true`, a promocao continua elegivel mas nao exigiria copia fisica
# se `has_conflict=true`, a promocao esta bloqueada por colisao com conteudo diferente no destino
# `conflict_reason=destination_content_mismatch` identifica esse conflito de forma estavel
# `eligibility_code` resume o motivo principal, por exemplo `eligible` ou `destination_conflict`
python3 -m app.services.curated_sources promote-candidate --candidate-id local-question-bank --confirm
python3 -m app.services.curated_sources list-candidates --review-decision approved
python3 -m app.services.curated_sources list-candidates --review-decision none
python3 -m app.services.curated_sources list-candidates --has-promotion-history true
python3 -m app.services.curated_sources list-candidates --has-promotion-history false
python3 -m app.services.curated_sources list-candidates --promotion-ready true
python3 -m app.services.curated_sources list-candidates --promotion-ready false
python3 -m app.services.curated_sources list-candidates --eligibility-code review_not_approved
python3 -m app.services.curated_sources list-candidates --eligibility-code eligible
python3 -m app.services.curated_sources list-candidates --destination raw_review
python3 -m app.services.curated_sources list-candidates --query react
python3 -m app.services.curated_sources list-candidates --has-artifact-path --limit 5
python3 -m app.services.curated_sources list-candidates --artifact-exists present --limit 5
python3 -m app.services.curated_sources list-candidates --origin local_file --limit 2 --json-lines
python3 -m app.services.curated_sources list-candidates --field candidate_id --field title
python3 -m app.services.curated_sources list-candidates --origin local_file --json-lines --field candidate_id --field artifact_path
python3 -m app.services.curated_sources list-candidates --compact --limit 3
python3 -m app.services.curated_sources list-candidates --compact --field candidate_id --field title --limit 3
```

- `candidate-stats` agora tambem resume decisoes humanas em `by_review_decision`, com buckets `approved`, `rejected`, `needs_revision` e `none`.
- `candidate-stats` agora tambem resume presenca de historico de promocao em `by_promotion_history`, com buckets `with_history` e `without_history`.
- `candidate-stats` agora tambem expõe `promotion_readiness`, resumindo quantos candidatos estao prontos ou nao para promocao manual com base no preflight real; isso nao promove nada.
- `candidate-stats` agora tambem expõe `promotion_blockers`, resumindo os principais `eligibility_code` dos candidatos `not_ready`; isso nao muda nada, e serve so para inspecao operacional.

**Comandos Canonicos**

Uso diario minimo do fluxo real:

```bash
# 1. revisar rapidamente um candidato
python3 -m app.services.curated_sources review-candidate --candidate-id local-question-bank --compact

# 2. registrar a decisao humana explicita
python3 -m app.services.curated_sources record-review-decision --candidate-id local-question-bank --decision approved --notes "manual review ok"

# 3. confirmar no preflight se a promocao pode seguir
python3 -m app.services.curated_sources check-promotion --candidate-id local-question-bank --compact

# 4. ver quais candidatos ja estao prontos
python3 -m app.services.curated_sources list-candidates --promotion-ready true --compact

# 5. promover manualmente com confirmacao explicita
python3 -m app.services.curated_sources promote-candidate --candidate-id local-question-bank --confirm

# 6. inspecionar historico curto de promocao
python3 -m app.services.curated_sources show-promotion-log --candidate-id local-question-bank --compact
```

**Troubleshooting Operacional**

- `eligibility_code` mostra o motivo principal calculado pelo preflight real.
- `eligibility_code=eligible` significa que o candidato esta apto para seguir no fluxo manual de promocao.
- Codigos como `review_not_approved`, `non_local_source`, `artifact_not_found` e `non_promotable_destination` indicam o bloqueio principal atual.
- `promotion_blockers` resume, de forma agregada, os motivos principais dos candidatos `not_ready`.
- Se `promotion_blockers.review_not_approved` dominar, o gargalo real esta em revisar e aprovar candidatos.
- Se aparecer `artifact_not_found`, o problema esta no artefato ou no caminho local.
- Se aparecer `non_promotable_destination`, o destino atual do candidato nao entra no nucleo promovivel desta versao.

Comandos uteis:

```bash
python3 -m app.services.curated_sources candidate-stats
python3 -m app.services.curated_sources list-candidates --eligibility-code review_not_approved
python3 -m app.services.curated_sources list-candidates --promotion-ready false --compact
```

**Acoes Recomendadas por Blocker**

- `review_not_approved`: revisar o candidato, registrar uma decisao humana explicita e, se fizer sentido, marcar `approved`.
- `artifact_not_found`: verificar `artifact_path`, confirmar se o arquivo ainda existe e corrigir o caminho ou restabelecer o artefato local.
- `missing_artifact_path`: preencher ou corrigir o artefato local associado ao candidato e confirmar que ele representa um arquivo local promovivel.
- `non_local_source`: confirmar se o candidato precisa virar artefato local antes da promocao; nao tentar promover diretamente fonte web/agregada.
- `non_promotable_destination`: revisar o `destination` e confirmar se o candidato deveria ir para `knowledge` ou `question_bank`.
- `destination_conflict`: revisar o arquivo ja existente no destino, comparar conteudo e decidir conscientemente antes de tentar nova promocao.
- Se `promotion_blockers.review_not_approved` dominar, o gargalo principal esta em revisao/aprovacao humana, nao em infraestrutura.

**Sequencia Recomendada de Diagnostico**

1. Ver o panorama geral:
   `python3 -m app.services.curated_sources candidate-stats`
   Use para enxergar `promotion_readiness`, `promotion_blockers` e identificar o gargalo dominante.
2. Isolar um grupo pelo motivo principal:
   `python3 -m app.services.curated_sources list-candidates --eligibility-code review_not_approved`
   Troque o `eligibility_code` conforme o blocker real que estiver dominando.
3. Inspecionar um candidato especifico:
   `python3 -m app.services.curated_sources review-candidate --candidate-id local-question-bank --compact`
   Use para ver rapidamente decisao humana, elegibilidade, conflito e historico curto.
4. Confirmar no preflight:
   `python3 -m app.services.curated_sources check-promotion --candidate-id local-question-bank --compact`
   Use para confirmar se ja pode promover e qual e o motivo principal atual.
5. So entao decidir a acao humana:
   revisar, aprovar, corrigir artefato, ajustar destino ou promover manualmente com `--confirm`.

Exportacao operacional minima:

```bash
python3 -m app.services.curated_sources list-candidates \
  --origin local_file \
  --has-artifact-path \
  --json-lines \
  > tmp/local_candidates.jsonl

python3 -m app.services.curated_sources list-candidates \
  --destination raw_review \
  --json-lines \
  --field candidate_id \
  --field artifact_path \
  > tmp/raw_review_candidates.jsonl
```

Registrar um candidato descoberto:

```bash
scripts/curated_sources.sh register-candidate \
  --title "FastAPI security guide" \
  --url "https://example.com/fastapi-security" \
  --discovered-from "awesome-fastapi" \
  --trust-level medium_trust \
  --destination raw_review
```

Registrar um candidato local a partir de artefato ja presente na curadoria:

```bash
scripts/curated_sources.sh register-candidate \
  --title "React Interview Questions Sudheer" \
  --artifact-path "data/raw_review/React_Interview_Questions_Sudheer.md" \
  --source-kind question_bank_material \
  --trust-level low_trust \
  --destination raw_review
```

- via `--url`, o candidato nasce com `source_origin=web`
- via `--artifact-path`, o candidato nasce com `source_origin=local_file`

Atualizar status de triagem:

```bash
scripts/curated_sources.sh set-status --candidate-id fastapi-security-guide-https-example-com-fastapi-security --status promoted
```

Politica detalhada:

- `INGESTION_POLICY.md`

Diagnostico simples de over-tagging na knowledge base:

```bash
scripts/knowledge_tag_diagnostics.sh --top 10 --pretty
```

Diagnostico de higiene do acervo knowledge:

```bash
scripts/knowledge_hygiene.sh --top 20 --pretty
curl "http://localhost:8000/api/knowledge/hygiene?top=20"
```

Regras desta comparacao:

- mantem `question_bank` e `knowledge` separados
- cruza apenas metadados inferidos (`inferred_tags`, `inferred_domain`, `inferred_subtheme`)
- classifica cobertura como `covered`, `partial` ou `missing`
- inclui `coverage_score`, `evidence_signals` e `reason` para explicar a decisao
- lista tags, dominios e subtemas mais carentes

## Importacao automatizada de downloads locais

Para importar materiais baixados manualmente de uma pasta de downloads para `data/knowledge_raw/`:

```bash
scripts/import_downloads.sh
```

Configuracao por ambiente:

- `DOWNLOADS_WATCH_DIR` - pasta monitorada. Padrao: `~/Downloads`
- `DOWNLOADS_IMPORT_MODE` - `copy` ou `move`
- `DOWNLOADS_NORMALIZE_NAMES` - `true` ou `false`
- `DOWNLOADS_TRIGGER_INGEST` - `true` ou `false`

Exemplo:

```bash
DOWNLOADS_WATCH_DIR=/tmp/my-downloads scripts/import_downloads.sh
```

Exemplos uteis:

```bash
scripts/import_downloads.sh --mode move
scripts/import_downloads.sh --no-ingest
scripts/import_downloads.sh --keep-names
scripts/import_downloads.sh --watch --poll-interval 10
```

O importador:

- valida extensoes suportadas
- calcula hash SHA-256
- evita duplicatas por conteudo
- copia ou move para `data/knowledge_raw/`
- pode normalizar o nome do arquivo
- pode disparar o parsing e o chunking logo depois

## Endpoints

- `GET /health` - status basico
- `POST /ingest` - envia texto simulado de fala
- `GET /api/knowledge/search?q=...&limit=5` - busca textual local nos chunks
- `GET /api/question-bank/search?q=...&limit=5` - busca textual local nos itens de avaliacao
- `GET /api/question-bank/coverage?top=10` - diagnostico de cobertura entre question_bank e knowledge
- `GET /api/question-bank/action-plan?top=10` - ranking pratico de ingestao juntando cobertura do question_bank e gap queue
- `GET /api/certifications/gap?q=...&track=python` - analise de lacuna por dominio de certificacao
- `GET /api/certifications/gap/plan?q=...&track=python` - analisa e registra lacuna para priorizacao de ingestao
- `GET /api/certifications/gap/queue?track=python&top=10` - consulta fila de prioridades de ingestao
- `GET /api/certifications/gap/queue?track=python&top=10&section=domains` - consulta segmentada (`all`, `gaps`, `topics`, `domains`, `certifications`)
- `GET /api/certifications/gap/queue?track=python&top=10&section=tags` - ranking de tags mais carentes (`tags-technology`, `tags-domain`, `tags-subtheme`)
- `GET /api/certifications/gap/queue?track=python&top=10&section=mismatch-top` - top desalinhamentos de track sugeridos para limpeza da base
- `WS /ws` - stream de snapshot de transcricao e sugestoes

Observacao sobre `POST /ingest`:
- o `snapshot` inclui `knowledge_context` com metadados internos da busca (`used_search`, `query`, `result_count`, `sources`) para auditoria sem expor chunk bruto na sugestao.

## Busca local de conhecimento

Busca textual inicial sobre os arquivos em `data/knowledge_chunks/`, sem dependencia de embeddings.
Agora com roteamento por tags tecnicas inferidas na ingestao (tecnologia, dominio e subtema), com fallback para busca global quando necessario.

CLI:

```bash
scripts/search_knowledge.sh "fastapi dependency injection" --limit 3
scripts/search_knowledge.sh "aws vpc subnet" --limit 5
scripts/search_knowledge.sh "explique herança em java" --limit 5
scripts/search_knowledge.sh "aws iam policy" --limit 5
scripts/search_knowledge.sh "linux firewall rules" --limit 5
```

Endpoint:

```bash
curl "http://localhost:8000/api/knowledge/search?q=linux+permissions&limit=3"
```

No retorno de busca e em `knowledge_debug`:

- `query_tags_inferred` / `query_tags_used`
- `used_tag_routing`
- `used_global_fallback`

## Mapa de certificacoes e analise de lacunas

Base inicial da trilha Python:

- `data/certifications/python_cert_map.json`
- certificacoes iniciais: `PCEP`, `PCAP`, `PCPP1`

CLI para analise:

```bash
scripts/analyze_cert_gap.sh "exceptions em python"
scripts/analyze_cert_gap.sh "modules e packages"
scripts/analyze_cert_gap.sh "object-oriented programming"
scripts/analyze_cert_gap.sh "web backend com python"
```

Endpoint para analise:

```bash
curl "http://localhost:8000/api/certifications/gap?q=exceptions+em+python&track=python"
```

Camada auxiliar de planejamento de ingestao:

- historico persistente: `data/certifications/gap_history.json`
- fila priorizada: `data/certifications/gap_queue.json`

CLI para registrar e consultar:

```bash
scripts/gap_queue.sh record "exceptions em python" --track python --pretty
scripts/gap_queue.sh record "modules e packages" --track python --pretty
scripts/gap_queue.sh report --track python --top 10 --pretty
scripts/gap_queue.sh report --track python --section topics --top 10 --pretty
scripts/gap_queue.sh report --track python --section domains --top 10 --pretty
scripts/gap_queue.sh report --track python --section tags --top 10 --pretty
scripts/gap_queue.sh report --track python --section tags-technology --top 10 --pretty
scripts/gap_queue.sh report --track python --section tags-domain --top 10 --pretty
scripts/gap_queue.sh report --track python --section tags-subtheme --top 10 --pretty
scripts/gap_queue.sh report --track python --section mismatches --top 10 --pretty
scripts/gap_queue.sh report --track python --section mismatch-top --top 10 --pretty
```

## O que esta mockado

- Transcricao: `app/services/transcription.py` usa `transcribe_mock()`.
- Sugestoes: `app/services/suggestions.py` usa heuristicas simples.
- Termos tecnicos: `app/services/terms.py` usa um dicionario minimo.

## Proximos passos sugeridos

1) Captura de audio real
- Integrar uma fila de audio com `sounddevice` ou `pyaudio`.
- Criar um processo de chunking e VAD (voice activity detection).

2) Transcricao real
- Trocar `transcribe_mock()` por um pipeline ASR local ou API externa.
- Isolar em `app/services/transcription.py` mantendo a mesma assinatura.

3) Modelo de IA e memoria
- Adicionar um servico de geracao com LLM (local ou API).
- Evoluir `app/services/context.py` para sumarizacao curta.
- Adicionar cache e limites de latencia.
