# MACHINE LEARNING — Corpus Raw Report

## Document count
- 4 páginas oficiais autorizadas pelo manifesto.

## Arquivos criados
- `data/knowledge_raw/machine_learning/framework_user_guide/user_guide_html.html`
- `data/knowledge_raw/machine_learning/framework_user_guide/user_guide_html.metadata.json`
- `data/knowledge_raw/machine_learning/framework_reference/index_html.html`
- `data/knowledge_raw/machine_learning/framework_reference/index_html.metadata.json`
- `data/knowledge_raw/machine_learning/framework_guide/guide.html`
- `data/knowledge_raw/machine_learning/framework_guide/guide.metadata.json`
- `data/knowledge_raw/machine_learning/educational_course/crash_course.html`
- `data/knowledge_raw/machine_learning/educational_course/crash_course.metadata.json`

## Categorias materializadas
- framework user guide
- framework reference
- framework guide
- educational course

## Domínios usados
- scikit-learn.org
- pytorch.org
- tensorflow.org
- developers.google.com

## Observações da captura
- O crawler oficial (`scripts/corpus/manifest_crawler.py`) consumiu as quatro URLs do manifest sem erros e salvou o HTML bruto juntamente com os arquivos de metadados requeridos.
- Cada metadata JSON registra `url`, `domain`, `download_timestamp`, `content_hash` e `content_type`, garantindo rastreabilidade para futuros parsers.
- Os artefatos permanecem isolados em `data/knowledge_raw/machine_learning/` e não misturam nenhum conteúdo de outras frentes.

## Confirmações
- Nenhum parsing, chunking, embedding ou baseline foi executado nesta etapa; a frente permanece em `corpus_raw_ready`.
- Todas as capturas foram feitas dentro do domínio autorizado do manifesto e nenhum erro crítico ocorreu durante o download.
