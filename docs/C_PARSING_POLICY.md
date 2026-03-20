# C Parsing Policy

Este documento formaliza o conjunto de operações de parsing/limpeza aplicadas ao corpus bruto de C (`data/knowledge_raw/c/`) antes de qualquer chunking ou ingestão vetorial.

## Objetivos comuns
- preservar títulos, seções e blocos explicativos que respondem a perguntas conceituais.
- remover metadata de navegação (menus, rodapés, links repetidos) e front matter que contaminam o ranking.
- deixar cada saída em texto plano legível, com espaçamento controlado e sem repetições de header/footer.

## 1. PDFs normativos (WG14)
- Ferramenta: `pdftotext -layout` para preservar colunas e títulos e evitar linhas embaralhadas.
- Política: manter capítulos, tabelas e anexos em texto puro, mas remover cabeçalhos/rodapés replicados manualmente durante a extração (p. ex., `nº 1` repetidos). O texto resultante é salvo em `data/knowledge_parsed/c/wg14/`.
- Observação: os PDFs carregam referências de página e notas de rodapé; a próxima etapa pode refinar ainda mais (ex: compressão de tabelas) se o chunking exigir.

## 2. HTML técnico (POSIX / Open Group)
- Ferramenta: script Python com `BeautifulSoup`.
- Política: eliminar tags de navegação (`nav`, `header`, `footer`, `aside`), scripts, stylesheets e qualquer elemento cujo `class` contenha `nav`, `menu`, `sidebar`, `breadcrumb`, `links` ou `path`.
- Preservar os blocos `h1–h6`, `p`, `pre`, `li`, `dt`, `dd` e tabelas relevantes. O texto é concatenado com quebras de linha simples e salvo em `data/knowledge_parsed/c/posix_issue7/`.
- Benefícios: o parsing deixa apenas títulos (função, seção) e descrições (parágrafos e listas) úteis para retrieval.

## 3. Cppreference (HTML wiki)
- Mesma abordagem do HTML técnico acima, com foco adicional em remover a janela lateral do wiki e as tags de tradução (`div` com `id`/`class` contendo `mw-panel`, `siteNotice`, `central-featured`).
- As páginas `language` e `header` são convertidas e salvas em `data/knowledge_parsed/c/cppreference_c/`.
- O script garante que as assinaturas de funções (ex.: prototypes) e os exemplos permaneçam intactos.

## 4. Man-pages (troff/Groff)
- Ferramenta: `groff -mandoc -Tutf8` aplicada aos arquivos relevantes (`man3/printf.3` no release 6.02). O output tem seções `NAME`, `SYNOPSIS`, `DESCRIPTION`, etc.
- Política: capturar apenas os blocos explicativos e reorganizar o texto em parágrafos claros; tabelas do troff aparecem como texto simplificado, o que ajuda o chunking.
- Nota: o comando emite alerta sobre `tbl`, mas o conteúdo verbal é preservado.

## 5. Generalidades
1. Cada parsing grava artefatos em `data/knowledge_parsed/c/<fonte>/` com extensão `.txt`.
2. O script registra as transformações; quaisquer atualizações no lockfile exigem reprocessamento e revalidação.
3. Nenhum chunkagem/vetor é gerado nesta etapa; o foco é deixar o texto pronto para a próxima fase.
