# Livecopilot Architecture (Reanchor 2026-03-09)

## 1) Proposito principal do projeto
Livecopilot e um copiloto contextual em tempo real, apoiado por base tecnica semantica, banco de questoes e aprendizagem por lacuna, para responder rapido em cenarios de entrevista, troubleshooting e comunicacao tecnica.

Eixo principal oficial:
- copiloto contextual em tempo real
- uso de conhecimento tecnico preparado antes
- suporte a entrevista, resposta rapida e aprendizagem

## 2) Problema que o projeto resolve
Transformar contexto atual da conversa + base tecnica + sinais de lacuna em sugestoes curtas, auditaveis e uteis com baixa latencia.

## 3) Matriz de modulos

### Modulo 1: Realtime Copilot
Responsabilidades:
- captura/transcricao/contexto
- sugestao rapida
- baixa latencia
- UI/overlay/resposta curta

Ativos ja implementados:
- captura e transcricao: `app/services/audio_capture.py`, `app/services/transcription.py`
- estado e contexto de conversa: `app/services/state.py`, `app/services/context.py`
- sugestoes e respostas curtas: `app/services/suggestions.py`, `app/services/quick_replies.py`, `app/services/fillers.py`, `app/services/topics.py`
- superficie realtime/API/UI: `app/main.py`, `app/api/routes.py`, `app/templates/index.html`, `app/static/app.js`

### Modulo 2: Knowledge Core
Responsabilidades:
- corpus tecnico
- semantic search
- embeddings
- ranking
- `knowledge_search`

Ativos ja implementados:
- ingestao/parsing/chunking/index local: `app/services/knowledge_ingest.py`, `knowledge_parsers.py`, `knowledge_chunks.py`, `markdown_chunker.py`, `knowledge_imports.py`
- busca e ranking semantico/local: `app/services/knowledge_search.py`, `app/services/semantic_min_api.py`
- sinais semanticos e qualidade: `app/services/knowledge_tags.py`, `knowledge_hygiene.py`, `knowledge_tag_diagnostics.py`, `search_metrics.py`, `ranking_regression.py`
- scripts operacionais: `scripts/ingest_knowledge.sh`, `scripts/semantic-ingest`, `scripts/semantic-search`, `scripts/semantic_*`

### Modulo 3: Question Bank / Gap Learning
Responsabilidades:
- `question_bank_search`
- mismatch / tracks
- lacunas
- aprendizagem guiada

Ativos ja implementados:
- ingestao/metadata/itemizacao do question bank: `app/services/question_bank_ingest.py`, `question_bank_parsers.py`, `question_bank_items.py`, `question_bank_metadata.py`
- busca e priorizacao: `app/services/question_bank_search.py`, `question_bank_coverage.py`, `question_bank_action.py`
- gap learning e mismatch por trilha: `app/services/knowledge_gap_analyzer.py`, `gap_priority_queue.py`, `gap_priority_cli.py`, `certification_map.py`
- scripts operacionais: `scripts/ingest_question_bank.sh`, `scripts/question_bank_coverage.sh`, `scripts/question_bank_action.sh`, `scripts/gap_queue.sh`, `scripts/analyze_cert_gap.sh`

### Modulo 4: Interview / Response Mode
Responsabilidades:
- respostas curtas
- framing para entrevista
- contextualizacao rapida

Ativos ja implementados:
- composicao de resposta curta contextual com base semantica: `app/services/suggestions.py`
- respostas imediatas e fillers: `app/services/quick_replies.py`, `app/services/fillers.py`
- endpoint/snapshot para consumo direto em UI: `app/api/routes.py`, `app/services/state.py`

### Modulo 5: Ops / Runbook Mode
Responsabilidades:
- planos
- runbooks
- incidentes
- command events
- melhoria operacional

Ativos ja implementados:
- CLI operacional concentrado em: `scripts/livecopilot-k8s`
- capacidade existente: modos diagnose/plan/runbook, catalogo de planos, templates por `incident_type`, validacao de plano
- trilha de incidentes e eventos: start/note/close incident, timeline, incident report markdown, command event log
- metricas e melhoria continua: learning report, plan metrics, command metrics, suggest runbook improvements
- armazenamento local operacional: `var/incidents/`, `var/docs/`, `var/usage/`, `var/plans/`

## 4) Classificacao do que ja existe hoje
- Ja consolidado no nucleo do produto:
  - Realtime Copilot (Modulo 1)
  - Knowledge Core (Modulo 2)
  - Question Bank / Gap Learning (Modulo 3)
  - Interview / Response Mode (Modulo 4)
- Ja consolidado como modulo satelite forte:
  - Ops / Runbook Mode (Modulo 5)

## 5) Nucleo vs satelites vs backlog futuro
Nucleo do produto (centro oficial):
- Modulo 1 + Modulo 2 + Modulo 3 + Modulo 4
- Resultado esperado: resposta contextual em tempo real, fundamentada em base tecnica e lacunas

Modulos satelite (estrategicos, nao eixo unico):
- Modulo 5 (Ops / Runbook Mode)
- Papel: ampliar uso operacional e gerar aprendizado aplicado sem substituir o eixo principal do copiloto contextual

Backlog futuro (sem implementacao nesta rodada):
- melhoria de latencia ponta-a-ponta (captura -> sugestao)
- acoplamento mais forte entre snapshot realtime e ranking semantico
- calibracao continua de qualidade entre knowledge_search/question_bank_search e framing de entrevista
- integracao controlada do feedback de runbooks/incidentes como sinal auxiliar para recomendacao

## 6) Diagnostico historico resumido
- O projeto nasceu no eixo de conhecimento contextual (knowledge search + question bank + gap learning).
- A frente de runbooks/incidentes/comandos/metricas surgiu depois e cresceu com valor operacional real.
- Nao houve perda caotica de direcao: houve bifurcacao.
- Reancoragem oficial: runbooks/incidentes permanecem importantes, mas como modulo da matriz (Modulo 5), nao como eixo unico do produto.

## 7) Roadmap reorganizado

### Curto prazo (reancoragem no eixo principal)
- fortalecer captura/transcricao/contexto em tempo real no fluxo principal
- reduzir latencia e melhorar resposta instantanea curta
- integrar de forma mais direta o contexto da conversa com `knowledge_search` e `question_bank_search`
- manter modulo Ops ativo, sem expandi-lo acima do nucleo neste ciclo

### Medio prazo
- consolidar contratos entre Modulo 1-4 (realtime + knowledge + gap + interview framing)
- ampliar avaliacao de qualidade de resposta contextual com cenarios reais
- usar sinais do Modulo 5 como contexto complementar controlado (nao dominante)

### Longo prazo
- evoluir para uma matriz madura multi-modulo com prioridade permanente do nucleo contextual
- unificar observabilidade de qualidade por modulo (latencia, relevancia, cobertura de lacunas, utilidade pratica)
- expandir satelites sem comprometer o centro: copiloto contextual em tempo real orientado por conhecimento tecnico e aprendizagem
