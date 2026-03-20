# Handoff 2026-03-14 - Livecopilot Semantic DB Baseline Validation

## status final
concluido

## escopo da rodada
- validar funcionalmente o banco semantico real ja existente
- medir baseline simples de volume, coerencia e performance
- nao criar schema
- nao fazer ingestao massiva
- nao adicionar indices

## arquivos lidos
- `docs/SEMANTIC_DB_CONTEXT_REPORT.md`
- `STATUS.md`
- `app/services/semantic_min_api.py`
- `app/services/knowledge_search.py`
- `app/services/suggestions.py`
- `scripts/continuity_recall.py`
- `scripts/project_brain_query.py`
- `docs/HANDOFF_KNOWLEDGE_PIPELINE_STAGE_CLOSURE_20260313T045713Z.md`
- `docs/HANDOFF_SEMANTIC_PERSIST_OBSERVABILITY35_AUDIT_20260312.md`
- `docs/HANDOFF_KNOWLEDGE_PIPELINE_V2_SEMANTIC_VALIDATE_20260313T034545Z.md`

## volume e estrutura observados

### contagens reais
- `public.documents`: `279`
- `public.chunks`: `1248`
- `public.query_embedding_cache`: `42`
- `public.semantic_search_cache`: `36`
- `public.project_memory_chunks`: `135`

### tamanho aproximado
- `public.chunks`: `15 MB`
- `public.project_memory_chunks`: `1352 kB`
- `public.query_embedding_cache`: `520 kB`
- `public.documents`: `384 kB`
- `public.semantic_search_cache`: `120 kB`

### indices vetoriais
- nao encontrados
- estado atual:
  - sem `ivfflat`
  - sem `hnsw`
  - apenas `btree`/PK/unique

## validacao funcional - trilha principal (`chunks` + `documents`)

### caminho validado
- `app/services/suggestions.py`
- `app/services.semantic_min_api.semantic_search()`
- consulta real em `public.chunks` com `JOIN public.documents`
- operador vetorial: `<=>`
- score exposto: `1 - distance`
- cache:
  - `query_embedding_cache`
  - `semantic_search_cache`

### queries testadas

#### 1. `docker host network`
- top-1:
  - `docker_docs_selected/content/manuals/engine/network/drivers/host.md`
- top-2:
  - `docker_docs_selected/content/manuals/engine/network/_index.md`
- top-3:
  - `docker_docs_selected/content/manuals/engine/network/drivers/_index.md`
- scores top-3:
  - `0.607465`
  - `0.517544`
  - `0.514528`
- leitura:
  - ranking coerente
  - a query bateu direto no documento `host.md`, que e o alvo esperado
- fallback lexico:
  - nao ocorreu

#### 2. `postgres auth`
- top-1:
  - `knowledge-gap::gap_20260310t234013_4528790000_1706c7323efb_postgres_auth.md`
- top-2:
  - `codex_docs_selected/docs/authentication.md`
- top-3:
  - `observability_docs_selected/alertmanager/docs/https.md`
- scores top-3:
  - `0.66058`
  - `0.415351`
  - `0.399616`
- leitura:
  - top-1 faz sentido
  - top-2 e top-3 mostram ruido semantico e queda rapida de aderencia
  - o ranking e parcialmente coerente, mas pouco robusto para termos curtos/genericos
- fallback lexico:
  - nao ocorreu

#### 3. `knowledge gap engine v1`
- top-1:
  - `knowledge-gap::gap_20260310t232657_6343290000_ce3a020227ec_validation_gap_ingestion_flow_kubernetes_network_policy_baseline.md`
- top-2:
  - `knowledge-gap::gap_20260310t234507_3291540000_4e3b1d6abc47_gap_flow_validation_ingress_nginx_timeout_504.md`
- top-3:
  - `data/raw_review/ckad_exercises_modules/f.services.md`
- scores top-3:
  - `0.403491`
  - `0.354062`
  - `0.338378`
- leitura:
  - ranking fraco para handoff/projeto
  - nao recuperou diretamente o handoff esperado
  - indica que a trilha principal e mais forte para corpus tecnico ingerido do que para memoria operacional do projeto
- fallback lexico:
  - informacao nao encontrada no estado atual do projeto para essa query no caminho `suggestions.py`, porque o gating nem chegou a disparar busca

#### 4. `mikrotik connected devices`
- top-1:
  - `docker_docs_selected/.../macvlan.md`
- top-2 e top-3:
  - question bank de networking
- scores top-3:
  - `0.312487`
  - `0.302468`
  - `0.302468`
- leitura:
  - ranking incoerente para o dominio pedido
  - evidencia ausencia de corpus aderente e falta de threshold/abstencao semantica mais dura
- fallback lexico:
  - nao ocorreu

## validacao funcional - trilha `project_memory_chunks`

### caminhos validados
- `scripts/continuity_recall.py`
- `scripts/project_brain_query.py`

### query `postgres`
- `continuity_recall.py` trouxe:
  - hits textuais coerentes para `Autenticacao peer no PostgreSQL local`
  - hits semanticos coerentes, mas com similaridade moderada (`~0.35`)
- `project_brain_query.py --query \"postgres auth\" --mode semantic` trouxe:
  - facts/runs coerentes sobre `Autenticacao peer no PostgreSQL local`
  - top semantic hits todos do tipo `fact`
  - similaridade observada: `~0.4599`
- leitura:
  - trilha de continuidade funciona melhor para memoria operacional do proprio projeto do que a trilha principal

### query `handoff`
- `continuity_recall.py --search handoff --semantic` nao trouxe `text_hits`
- os `semantic_hits` foram fracos e puxaram itens genericos de continuidade/checkpoint (`~0.24-0.25`)
- leitura:
  - para `handoff` isolado a memoria operacional nao esta bem ancorada
  - o corpus de `project_memory_chunks` privilegia facts/checkpoints/run summaries, nao o catalogo integral de handoffs

### query `checkpoint continuidade`
- `project_brain_query.py --query \"checkpoint continuidade\" --mode semantic` trouxe:
  - varios facts `checkpoint`
  - top hits coerentes
  - similaridade observada: `~0.590-0.599`
- leitura:
  - bom comportamento para memoria recente/continuidade

## baseline simples de performance

### trilha principal
- `semantic_search(\"docker host network\")`:
  - primeira chamada `openai_fresh`: `~693 ms` wall
  - chamada com cache de resposta: `~37.6 ms` wall
  - `semantic_duration_ms` com cache: `20 ms`
- `semantic_search(\"postgres auth\")`:
  - primeira chamada `openai_fresh`: `~2493 ms` wall
  - chamada com cache de resposta: `~832.8 ms` wall
  - `semantic_duration_ms` com cache: `24 ms`
- `semantic_search(\"mikrotik connected devices\")`:
  - com cache de resposta: `~69.6 ms` wall
  - `semantic_duration_ms`: `45 ms`

Leitura:
- o custo dominante da primeira chamada e geracao de embedding/OpenAI
- com cache, o banco em si responde rapido no tamanho atual
- a diferenca entre wall time e `semantic_duration_ms` indica overhead Python/processo/import alem do SQL

### trilha `project_memory_chunks`
- `continuity_recall.py --search postgres --semantic`: `~1976.6 ms` wall
- `continuity_recall.py --search handoff --semantic`: `~1638.8 ms` wall
- `project_brain_query.py --query \"postgres auth\" --mode semantic`: `~1725.3 ms` wall
- `project_brain_query.py --query \"checkpoint continuidade\" --mode semantic`: `~1693.3 ms` wall

Leitura:
- o custo dominante tambem parece ser embedding/OpenAI + startup de script
- o dataset de `project_memory_chunks` e pequeno; o gargalo hoje nao parece ser leitura SQL

## explain simples

### trilha principal (`chunks`)
- plano observado:
  - `Seq Scan on chunks`
  - `Seq Scan on documents`
  - `top-N heapsort`
- tempo observado:
  - `Execution Time: 57.988 ms`
- leitura:
  - ha `seq scan` completo em `chunks`
  - no volume atual (`1248` linhas) ainda e toleravel

### trilha `project_memory_chunks`
- plano observado:
  - `Seq Scan on project_memory_chunks`
  - `Index Scan` em `project_runs` por `project_name`
  - `Seq Scan` em `query_embedding_cache`
  - `top-N heapsort`
- tempo observado:
  - `Execution Time: 7.428 ms`
- leitura:
  - tambem opera por `seq scan`
  - no volume atual (`135` linhas) esta barato

## comparacao dos dois trilhos

### para que serve `public.chunks` hoje
- base semantica principal do app
- corpus tecnico/documental ingerido (`documents` + `chunks`)
- atende melhor perguntas sobre conteudo tecnico aderente ao corpus

### para que serve `public.project_memory_chunks` hoje
- memoria operacional/continuidade do proprio projeto
- runs, facts e checkpoints
- atende melhor consultas sobre historico recente e estado operacional

### overlap
- existe overlap parcial no tema `PostgreSQL`, porque o projeto registra fatos operacionais e tambem possui documentos relacionados
- nao sao bases equivalentes

### adequacao por caso
- conhecimento geral do projeto:
  - melhor candidato hoje: `public.chunks` quando o assunto estiver realmente no corpus documental ingerido
- continuidade operacional:
  - melhor candidato hoje: `public.project_memory_chunks`
- memoria recente:
  - melhor candidato hoje: `public.project_memory_chunks`

## conclusao tecnica

### a busca semantica principal ja esta funcional?
- sim
- esta funcional para consultas aderentes ao corpus

### os resultados fazem sentido?
- sim, quando a query e bem alinhada ao corpus (`docker host network`)
- parcialmente, quando a query e curta/generica (`postgres auth`)
- nao, quando falta corpus aderente ou threshold de abstencao (`mikrotik connected devices`)

### a ausencia de indice vetorial ja e gargalo provavel?
- ainda nao parece ser o gargalo principal no volume atual
- o maior custo observado nesta rodada foi:
  - geracao de embedding/OpenAI
  - startup de processo/script
- o banco esta fazendo `seq scan`, mas os tempos SQL ainda estao baixos no tamanho atual

### principal gargalo percebido
- qualidade/coerencia do ranking fora do dominio aderente
- falta de threshold de abstencao mais duro para evitar falso positivo semantico
- separacao ainda nao resolvida entre trilha documental (`chunks`) e trilha operacional (`project_memory_chunks`)

## proximo passo recomendado
- passo mais racional agora:
  - validar e ajustar qualidade de ranking/abstencao antes de indexar
- ordem recomendada:
  1. definir criterio minimo de coerencia/threshold para a trilha principal
  2. decidir explicitamente quando consultar `chunks` vs `project_memory_chunks`
  3. so depois reavaliar indice vetorial, se o volume crescer ou a latencia SQL subir

## riscos de mexer sem contexto
- adicionar indice vetorial agora sem baseline comparavel pode otimizar o lugar errado
- unificar trilhos sem contrato de uso pode misturar documento tecnico com memoria operacional recente
- mexer no chunking/ranking sem preservar casos coerentes atuais pode piorar consultas boas como `docker host network`

## se precisa aprovacao
nao

## se houve erro
- nao houve erro bloqueante
- observacao operacional:
  - `project_brain_query.py --format json` emite linha extra de log antes do JSON; isso nao quebra o uso humano, mas atrapalha parse automatizado estrito
