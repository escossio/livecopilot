# Handoff: primeiro ciclo controlado de aquisicao por clone oficial (Docker)

Data: 2026-03-11
Escopo: clone controlado + diagnostico de estrutura (sem ingestao)

## O que foi executado
1. Caminho canonico de aquisicao criado:
   - `data/knowledge_raw/_official_repo_clones/docker-docs`
2. Clone oficial executado (controlado):
   - `git clone --depth 1 https://github.com/docker/docs.git data/knowledge_raw/_official_repo_clones/docker-docs`
3. Mapeamento estrutural do repositorio e auditoria de aderencia aos gaps priorizados.

## Estrutura principal encontrada (resumo)
- Raiz: repo de docs completo com Hugo/estrutura editorial (`content/`, `assets/`, `layouts/`, `data/`).
- Conteudo documental principal em markdown: `content/`.
- Volume total:
  - tamanho local aproximado: `79M`
  - markdown total no repo: `1259`
  - markdown em `content/`: `1113`
  - nao-markdown: `998` (assets/config/scripts etc.)

## Areas mais valiosas para o banco semantico (foco desta rodada)
Recorte recomendado de alto valor tecnico para os gaps alvo:
- `content/manuals/build/building` (9 md)
  - inclui `multi-stage.md`, `best-practices.md`
- `content/manuals/build/buildkit` (4 md)
- `content/manuals/build/cache` (11 md)
- `content/manuals/engine/network` (14 md)
- `content/manuals/engine/storage` (14 md)
  - inclui `volumes.md`
- `content/manuals/engine/security` (18 md)
- `content/manuals/security` (9 md)

Total do recorte recomendado: `79` arquivos `.md`.

## Qualidade/limpeza para ingestao
- O repositorio e tecnicamente confiavel e oficial, mas nao e "limpo" no sentido de texto puro:
  - usa frontmatter YAML em massa;
  - usa shortcodes Hugo (`{{< ... >}}`, `{{% ... %}}`) em varios arquivos;
  - inclui muitos assets e itens nao-doc.
- Diagnostico objetivo:
  - **nao** recomendado ingestao total cega do repo clonado;
  - **recomendado** ingestao seletiva do recorte acima.

## Veredito de ingestao
- Ingestao total do clone: **nao recomendada** para este ciclo inicial.
- Ingestao seletiva (79 md do recorte): **recomendada**.

## Proximo comando canônico sugerido (nao executado nesta rodada)
Preparar recorte para ingestao local-first sem mudar pipeline:

```bash
mkdir -p data/knowledge_raw/docker_docs_selected && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/build/building/ \
  data/knowledge_raw/docker_docs_selected/build/building/ && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/build/buildkit/ \
  data/knowledge_raw/docker_docs_selected/build/buildkit/ && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/build/cache/ \
  data/knowledge_raw/docker_docs_selected/build/cache/ && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/engine/network/ \
  data/knowledge_raw/docker_docs_selected/engine/network/ && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/engine/storage/ \
  data/knowledge_raw/docker_docs_selected/engine/storage/ && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/engine/security/ \
  data/knowledge_raw/docker_docs_selected/engine/security/ && \
rsync -a --prune-empty-dirs \
  --include '*/' --include '*.md' --exclude '*' \
  data/knowledge_raw/_official_repo_clones/docker-docs/content/manuals/security/ \
  data/knowledge_raw/docker_docs_selected/security/
```

Depois, quando aprovado:

```bash
scripts/ingest_knowledge.sh
```

## O que nao mudou
- Nenhuma alteracao de pipeline.
- Nenhuma alteracao em `knowledge_parsers`, `knowledge_chunks` ou persistencia semantica.
- Nenhuma ingestao executada nesta rodada.
