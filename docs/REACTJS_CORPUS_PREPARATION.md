# ReactJS Corpus Preparation

## Objetivo da preparação de corpus
- Capturar os conteúdos oficiais do React (core, componentes, props/state, hooks, effects e renderização) para montar um corpus raw íntegro antes de avançar para parsing.

## Estratégia de ingestão
- Priorizar o domínio `react.dev`, navegando pelos capítulos de learn, guia e referência que cobrem os tópicos permitidos em `docs/FRONT_REACTJS.md`.
- Extrair HTML/markdown bruto mantendo o mapeamento de seções, exemplos e APIs, com registros de `source_url`, `captured_at` e `hash`.
- Validar cada URL contra o manifesto oficial antes de materializar o arquivo em `data/knowledge_raw/reactjs/`.

## Tipos de conteúdo permitidos
- Capítulos do React Dev Learn sobre componentes, props/state, hooks, efeitos, renderização e fluxos recomendados.
- Referências oficiais de APIs e ciclo de vida (`react.dev/reference/react`), incluindo Hooks e utilitários da equipe React.
- Guias de boas práticas, performance e renderização incremental publicados diretamente em `react.dev`.

## Tipos de conteúdo proibidos
- Artigos de terceiros, vídeos, cursos pagos ou contribuições comunitárias que não estejam sob o controle editorial do React Team.
- Conteúdos experimentais não oficiais ou extensões mantidas fora do domínio `react.dev`.

## Estrutura esperada do corpus raw
- Diretório raiz: `data/knowledge_raw/reactjs/`
- Subfocos sugeridos: `learn/`, `reference/`, `hooks/`, `render/`, `guides/`.
- Cada item armazenado como markdown padronizado com metadados de origem (`source_url`, `captured_at`, `hash`, `notes`).

## Confirmação de status
- Nenhuma ingestão, parsing, chunking ou embedding foi executada; este documento apenas descreve o planejamento da etapa `corpus_preparation`.
