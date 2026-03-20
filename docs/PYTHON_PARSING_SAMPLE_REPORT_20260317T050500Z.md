# Relatório de amostras — Parsing Python Lote 1 (2026-03-17T05:05:00Z)

## Método
- comparei o HTML bruto (`data/knowledge_raw/python/...`) com o parseado (`data/knowledge_parsed/python/...`) para quatro páginas representativas.

| Amostra | Origem bruta | Arquivo parseado | Removido | Mantido | Avaliação |
| --- | --- | --- | --- | --- | --- |
| Tutorial oficial | `tutorial/index.html` | `tutorial/index.html` | navegação superior, rodapé, sidebar lateral, breadcrumbs | títulos, seções introdutórias e trechos de código exemplares | texto mais direto, pronto para chunking por tópicos do tutorial |
| Language Reference | `language_reference/index.html` | `language_reference/index.html` | menus de versões, links de navegação e footer | sumário geral da gramática, headings de seções e blocos de definição | foco no conteúdo formal reduz ruído de UI |
| Built-in Functions | `builtins_exceptions/functions.html` | `builtins_exceptions/functions.html` | referências cruzadas repetidas e breadcrumb | assinaturas de funções e descrições completas | chunkável para cada built-in mantendo exemplos curtos |
| Módulo pathlib | `modules/pathlib/pathlib.html` | `modules/pathlib/pathlib.html` | barra lateral e notas de rodapé | explicações das classes Path, exemplos e links diretos | mais fácil de responder perguntas sobre APIs específicas |

## Conclusão rápida
- O parsing removeu consistentemente elementos decorativos e manteve o conteúdo essencial solicitado na política de parsing (`docs/PYTHON_PARSING_POLICY.md`).
- As versões parseadas agora vivem em `data/knowledge_parsed/python/` e podem ser usadas na próxima etapa de chunking controlado.
