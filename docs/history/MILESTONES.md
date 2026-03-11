# Milestones

## M1 — Fundação do MVP local
- **Marco:** criação da base executável (backend + UI + mock).
- **Descrição:** projeto nasce com arquitetura modular e fluxo de entrada simulada.
- **Impacto:** validação rápida de valor sem depender de voz real.
- **Dependências:** FastAPI/UI local, configuração por ambiente.

## M2 — Motor contextual inicial
- **Marco:** sugestões deixam de ser totalmente genéricas.
- **Descrição:** classificação simples de intenção/tema e respostas mais úteis.
- **Impacto:** salto de utilidade prática em entrevistas e conversa técnica.
- **Dependências:** dicionário inicial de temas técnicos.

## M3 — Memória de mercado
- **Marco:** ingestão de vagas (seed) e integração ao motor de sugestões.
- **Descrição:** termos recorrentes por frequência/categoria entram no contexto.
- **Impacto:** sistema passa a refletir sinais reais de mercado.
- **Dependências:** pipeline de ingestão de vagas + taxonomia.

## M4 — Knowledge base documental
- **Marco:** ingestão local de documentos (parse + chunk).
- **Descrição:** materiais técnicos passam a ser convertidos em base consultável.
- **Impacto:** respostas começam a usar suporte documental.
- **Dependências:** parsers, chunking, scripts de ingestão.

## M5 — Busca local com debug/explainability
- **Marco:** recuperação de chunks com inspeção de fontes e rastreio.
- **Descrição:** busca textual/ranqueada e integração ao fluxo de resposta.
- **Impacto:** menos "resposta no escuro", mais auditabilidade.
- **Dependências:** índice local de chunks + endpoint/CLI de busca.

## M6 — Camada de certificação e gap analyzer
- **Marco:** mapeamento por trilhas/domínios para diagnóstico de cobertura.
- **Descrição:** status `covered/partial/missing` por tema.
- **Impacto:** sistema mede lacunas com estrutura formal.
- **Dependências:** certification map + metadata inferida.

## M7 — Gap queue e action plan
- **Marco:** lacunas viram fila priorizada e ranking de ingestão.
- **Descrição:** prioridade por gravidade/recorrência e consolidação temática.
- **Impacto:** saída operacional para decidir o que ingerir depois.
- **Dependências:** coverage + gap queue + consolidação.

## M8 — Separação question_bank vs knowledge (consolidada)
- **Marco:** pipeline dedicado para questionários/provas.
- **Descrição:** parser higienizado, extração de itens, comparador com knowledge.
- **Impacto:** evita mistura semântica e melhora diagnóstico.
- **Dependências:** trilha de ingestão própria do question bank.

## M9 — Higiene do acervo e penalização de ranking
- **Marco:** documentos inconsistentes deixam de inflar evidência.
- **Descrição:** flags/score de higiene persistidos e usados no ranking/comparador.
- **Impacto:** melhora qualidade de recuperação sem perda de auditoria.
- **Dependências:** serviço `knowledge_hygiene` + integração no search/coverage.

## M10 — Realtime em fases (1 -> 3.5)
- **Marco:** evolução incremental do módulo realtime.
- **Descrição:** endpoint inicial, modos, ingest incremental, heurística de readiness, persistência de sessão, TTL e métricas.
- **Impacto:** operação realtime observável e mais robusta.
- **Dependências:** contratos de API, estado de sessão, telemetria.

## M11 — Hardening de qualidade semântica e EPUB
- **Marco:** higiene de acervo + chunking estruturado de EPUB.
- **Descrição:** flags de higiene persistidas, penalização de ranking, TOC legível, metadados por capítulo/seção e coerência de payload em EPUB.
- **Impacto:** redução de ruído de recuperação e aumento de explainability em fontes longas.
- **Dependências:** `knowledge_hygiene`, `knowledge_parsers`, `knowledge_chunks`, busca local.
