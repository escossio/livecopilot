# C Chunking Sample Report

Este relatório mostra como os chunks piloto ficaram mais limpos e reutilizáveis em cada tipo de fonte.

| Fonte | Arquivo parseado | Chunk gerado | O que foi removido | O que foi preservado | Avaliação |
| --- | --- | --- | --- | --- | --- |
| WG14 (N2756) | `data/knowledge_parsed/c/wg14/n2756.txt` | `data/knowledge_chunks/c/wg14/wg14-01.txt` (`1. INTRODUCTION`) | Cabeçalhos/rodapés e números de página da versão PDF | Texto introdutório sobre o modelo de memória concreta | Mantém a sequência argumentativa da seção; pronto para o ranking normativo |
| POSIX (stdio.h) | `data/knowledge_parsed/c/posix_issue7/stdio.h.txt` | `data/knowledge_chunks/c/posix_issue7/posix_issue7-01.txt` | Scripts/navegação HTML | Nome, sinopse, descrição da função e macros | Foco total na especificação da API; chunk responde diretamente a perguntas sobre `<stdio.h>` |
| Cppreference (language) | `data/knowledge_parsed/c/cppreference_c/language.txt` | `data/knowledge_chunks/c/cppreference_c/cppreference_c-01.txt` (`Expressions`) | Navbar/wiki chrome e blocos [edit] | Lista de subtemas da seção Expressions | Apresenta os tópicos que devem ser priorizados em respostas conceituais |
| Cppreference (headers) | `data/knowledge_parsed/c/cppreference_c/header.txt` | `data/knowledge_chunks/c/cppreference_c/cppreference_c-02.txt` (`<complex.h>`) | links de edição e navegação | Descrição do propósito do header e nota de versão | Chunk tem meta descritiva e contextualiza o header para perguntas de biblioteca |
| Man-pages (printf.3) | `data/knowledge_parsed/c/man7/printf-3.txt` | `data/knowledge_chunks/c/man7/man7-01.txt` (`NAME`) | Sequências ANSI/troff | Nome e resumo das funções printf-family | Preserva o resumo padrão do manual, garantindo chunk pronto para perguntas de referência |

Essas amostras serão usadas para validar a qualidade do chunking antes de expandir para mais fontes ou iniciar embeddings.
