# Azure Corpus Preparation

## Objetivo da preparação de corpus
- Consolidar os conteúdos oficiais do Azure (serviços core, compute, networking, storage, identidade e CLI) em um repositório raw controlado, garantindo rastreabilidade antes de qualquer parsing.

## Estratégia de ingestão
- Priorizar páginas atualizadas e canonizadas em `learn.microsoft.com` que cubram os tópicos listados no escopo de `docs/FRONT_AZURE.md`.
- Capturar HTML/markdown bruto com metadados `source_url`, `captured_at` e `hash`, mantendo a hierarquia de seções e cabeçalhos oficiais.
- Validar cada URL contra o manifesto oficial antes de adicionar ao corpus e registrar o registro de captura em `data/knowledge_raw/azure/`.

## Tipos de conteúdo permitidos
- Documentação técnica hospedada sob `learn.microsoft.com` e subdomínios `microsoft.com` que contenham guias oficiais (architecture, compute, networking, storage, identity, CLI). 
- Tópicos com descrições de arquiteturas, comandos do `az`, referências de APIs, diagramas oficiais e guias de boas práticas publicados pela Microsoft.

## Tipos de conteúdo proibidos
- Blogs externos, artigos de opinião, marketing e materiais de parceiros sem vínculo direto com os repositórios oficiais da Microsoft.
- Releases ou changelogs não assinados oficialmente e conteúdos duplicados sem manutenção de versão oficial.

## Estrutura esperada do corpus raw
- Diretório raiz: `data/knowledge_raw/azure/`
- Possíveis subdivisões: `architecture/`, `compute/`, `networking/`, `storage/`, `identity/`, `cli/`.
- Cada documento será armazenado em markdown normalizado com metadados JSON com `source_url`, `captured_at`, `hash` e `notes`.

## Confirmação de status
- Nenhuma etapa de ingestão, parsing, chunking ou embedding foi executada até o momento; este documento apenas descreve o plano de preparação inicial.
