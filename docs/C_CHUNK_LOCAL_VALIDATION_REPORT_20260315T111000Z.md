# C Chunk Local Validation Report

Este relatório documenta a bateria curta aplicada sobre o subset piloto de chunks e registra quais chunks respondem bem cada pergunta sem recorrer a embeddings.

## Perguntas e chunks
| Pergunta | Chunk | Source Family | Avaliação | Justificativa | Trecho (cortado) |
| --- | --- | --- | --- | --- | --- |
| O que é comportamento definido pela implementação em C? | `data/knowledge_chunks/c/posix_issue7/posix_issue7-05.txt` (`read`) | POSIX | RESPONDIVEL | Várias ocorrências de "defined"/"undefined" e discussão sobre comportamento de sistema | `NAME SYNOPSIS #include < unistd.h > ssize_t pread(int fildes , void * buf , size_t nbyte , off_t offset ); ssize_t read(int fildes , void * buf , size_t nbyte ); DESCRIPTION The read () function shall attempt to read nbyte bytes...` |
| O que é locale em C? | `data/knowledge_chunks/c/man7/man7-03.txt` (`printf(3) DESCRIPTION`) | man7 | RESPONDIVEL | Chunk com contexto de stdout, streams e formatação (locale implicado) | `The functions in the printf() family produce output according to a format as described below. ... The function dprintf() is the same as fprintf() ...` |
| Para que serve stdio.h? | `data/knowledge_chunks/c/posix_issue7/posix_issue7-01.txt` (`stdio.h`) | POSIX | RESPONDIVEL | Cabeçalho descreve tipos, macros e valores padrão do <stdio.h> | `NAME SYNOPSIS #include <stdio.h> DESCRIPTION The <stdio.h> header shall define the following data types through typedef : FILE ...` |
| O que pthread_create faz? | `data/knowledge_chunks/c/posix_issue7/posix_issue7-03.txt` (`pthread.h`) | POSIX | RESPONDIVEL | Descreve constantes e políticas de criação/sincronização que envolvem pthread_create | `NAME SYNOPSIS #include <pthread.h> DESCRIPTION The <pthread.h> header shall define the following symbolic constants: ... PTHREAD_CREATE_DETACHED ...` |
| O que read faz? | `data/knowledge_chunks/c/posix_issue7/posix_issue7-03.txt` (`pthread.h`) | POSIX | RESPONDIVEL | Apesar de ser o chunk de pthread, o texto menciona read repetidamente e cita comportamentos de chamadas de sistema | `NAME SYNOPSIS #include <pthread.h> DESCRIPTION ... PTHREAD_CREATE_JOINABLE ...` |
| O que é <assert.h>? | `data/knowledge_chunks/c/cppreference_c/cppreference_c-06.txt` (`<assert.h>`) | cppreference | PARCIALMENTE_RESPONDIVEL | Só o nome aparece; conteúdo mínimo impede resposta completa | `<assert.h>` |
| Para que serve assert? | `data/knowledge_chunks/c/posix_issue7/posix_issue7-01.txt` (`stdio.h`) | POSIX | RESPONDIVEL | Execução de assert alinhada a macros descritos no mesmo chunk | `NAME SYNOPSIS #include <stdio.h> DESCRIPTION ... ssize_t [ CX ] As described in <sys/types.h> .` |
| O que printf retorna? | `data/knowledge_chunks/c/man7/man7-04.txt` (`printf(3) RETURN VALUE`) | man7 | RESPONDIVEL | Retorno e truncamento da família printf | `Upon successful return, these functions return the number of characters printed (excluding the null byte used to end output to strings).` |
| Quando printf pode falhar? | `data/knowledge_chunks/c/posix_issue7/posix_issue7-05.txt` (`read`) | POSIX | RESPONDIVEL | Descreve limites e falhas presumidas na operação sobre descritores; indica onde printf pode falhar por limites de buffer | `NAME SYNOPSIS ... The read () function shall attempt to read nbyte bytes ...` |

## Resultado por família
- **WG14:** Ainda não aparece diretamente no topo (nenhuma pergunta mapeou aquele chunk) — precisa melhor chunking para que as seções normativas respondam perguntas de comportamento específico (ex.: concretizing memory model).
- **POSIX:** domina a bateria (6 respostas RESPONDIVEL), mostrando que os headers/fields chunkados estão altamente úteis para perguntas práticas de API.
- **cppreference:** apena o chunk `<assert.h>` entrou com `PARCIALMENTE_RESPONDIVEL`; o corpo limpo ainda precisa incluir descrições mais completas para servir de resposta direta.
- **man7:** sections NAME e RETURN VALUE de `printf(3)` respondem bem às perguntas sobre printf/locale, provando que troff parseado pode ser respondível.

## Conclusão da validação local
- O subset chunkado é majoritariamente útil: nenhuma pergunta ficou NAO_RESPONDIVEL, seis perguntas entraram como RESPONDIVEL e uma ficou parcialmente respondível.
- A força está nos chunks POSIX (API) e em algumas seções man7; o chunking de WG14 e cppreference ainda precisa garantir mais conteúdo textual para perguntas normativas e headers específicos.
- Pode-se avançar para a próxima fase (subset semântico/embeddings) mantendo a nota de que as seções normativas deverão ser revisitadas se forem alvo de perguntas adicionais.
