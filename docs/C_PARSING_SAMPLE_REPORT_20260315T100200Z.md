# C Parsing Sample Report

Documenta as amostras comparativas antes/depois para cada tipo de fonte do corpus C. O objetivo é evidenciar que o parseado ficou mais limpo e pronto para chunking subsequente.

| Fonte | Arquivo bruto | Arquivo parseado | O que foi removido | O que foi preservado | Avaliação |
| --- | --- | --- | --- | --- | --- |
| WG14 PDF (norma C17) | `data/knowledge_raw/c/wg14/n2610.pdf` | `data/knowledge_parsed/c/wg14/n2610.txt` | Cabeçalhos/rodapés repetidos, números de página e notas de rodapé descontextualizadas | Títulos de capítulo (ex.: "1. Introduction"), cláusulas de sintaxe e blocos explicativos | Texto plano manteve a hierarquia seções + definições; mais chunkável porque não há números de página no meio. |
| POSIX HTML (`stdio.h`) | `data/knowledge_raw/c/posix_issue7/stdio.h.html` | `data/knowledge_parsed/c/posix_issue7/stdio.h.txt` | Barra lateral, banner, menus e links de navegação (header/footer) | Cabeçalho da função, descrições, listas de argumentos e notas de atributos | Parseado foca apenas no conteúdo técnico imediato; elimina ruído de menu e repetição de rodapé, facilitando chunking por parágrafos. |
| Cppreference `language` | `data/knowledge_raw/c/cppreference_c/language` | `data/knowledge_parsed/c/cppreference_c/language.txt` | Painel lateral do wiki, links de ajuda, controles de tradução e a caixa "From C++" | Títulos de seção, protótipos de sintaxe, exemplos explicativos | Resultado preserva exemplos, bullet points e notas; perdeu apenas o chrome da wiki, mantendo o texto útil. |
| Man-page `printf(3)` | `data/knowledge_raw/c/man7/man-pages-6.02/man3/printf.3` | `data/knowledge_parsed/c/man7/printf-3.txt` | Macro-rodapé de tabela (avisos de tbl), controle de formatação (tbl/soelim) | Seções `NAME`, `SYNOPSIS`, `DESCRIPTION`, `RETURN VALUE`, `EXAMPLES` | Parseado ficou mais linear, sem roff cru; as seções úteis agora aparecem em blocos textuais claros prontos para chunking. |
