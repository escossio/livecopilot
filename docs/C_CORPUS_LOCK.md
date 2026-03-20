# C Corpus Lock

Registra o estado congelado do corpus bruto de C (dados armazenados em `data/knowledge_raw/c/`). Serve como lockfile operacional antes de qualquer parsing/chunking.

## Snapshot metadata
- Manifesto usado: `docs/C_SOURCE_MANIFEST.md` + `docs/C_SOURCE_MANIFEST.json`
- Timestamp da coleta: 2026-03-15T22:24:00-03:00 (UTC-3)
- Director root: `data/knowledge_raw/c/`

## Fonte: ISO/IEC 9899:2018 (C17) via WG14
| Categoria | Formato | Caminho local | Hash SHA256 | Nota |
| --- | --- | --- | --- | --- |
| PRIMÁRIA | PDF | `data/knowledge_raw/c/wg14/n2610.pdf` | `3d53887943a58dd1016477a0987fe17357cf708168053f12e2cf1c6b277c6624` | Draft N2610 reproduz partes do C17; compra oficial ISO pendente. |
| PRIMÁRIA | PDF | `data/knowledge_raw/c/wg14/n2756.pdf` | `c76ce86b21a3639c62f7c3f00549487f31b84b15777b53610e4de0afd988a5d9` | Draft N2756 (C23) disponível publicamente para referência futura. |

## Fonte: The Open Group Base Specifications Issue 7 (POSIX.1-2017)
| Item | Categoria | Formato | Caminho local | Hash SHA256 | Nota |
| --- | --- | --- | --- | --- | --- |
| `stdio.h` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/stdio.h.html` | `c8d4abfa736c9833fde57e2581d8fe76e1563445d22756759de8e2cc671935aa` | Documentação oficial para `stdio` (capítulos 2/4). |
| `stdlib.h` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/stdlib.h.html` | `dbaf7e1a2b6648480ce07b4eabdf2e8fd80cdca1169a28e83d11ac9b71f41973` | Capítulo de biblioteca padrão. |
| `pthread.h` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/pthread.h.html` | `a6b03b86d0df916c07ea39457ae217bc52b3f75038838a3befc028f2eedc376f` | Threading e sincronização. |
| `unistd.h` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/unistd.h.html` | `6dd62a12af7ed4f68d36fe40a543329f5b070be76a36e411a3a310dc21b778a6` | Syscalls comuns e defines. |
| `printf(3)` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/printf.html` | `7b2aefab4c62ad91335c54816281d583f5a2157df8d9cca42dd6e4865a436211` | Função básica de saída. |
| `pthread_create(3)` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/pthread_create.html` | `eff09534f15a1b2a15e21278ad291b37f062304624dc33a8821baa5fd15cf2ee` | Criação de threads POSIX. |
| `read(2)` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/read.html` | `682603d03e467c5e10c3ddd672dfb6548270a8e0ffd809a458240cee72f17b02` | Cadastro de syscalls. |
| `exit(3)` | PRIMÁRIA | HTML | `data/knowledge_raw/c/posix_issue7/exit.html` | `b1a882fd05893babc784d7ba0bcaed3c01a6f635131d5984fbe590954404de45` | Finalização de processo. |

## Fonte: Cppreference (C language + headers)
| Categoria | Formato | Caminho local | Hash SHA256 | Nota |
| --- | --- | --- | --- | --- |
| SECUNDÁRIA | HTML | `data/knowledge_raw/c/cppreference_c/language` | `1e200674475ae2233102dc7dab3eab03bf3a09e6101a40dc09984c135f25de23` | Página `language` capturada via `wget` (sem clone). |
| SECUNDÁRIA | HTML | `data/knowledge_raw/c/cppreference_c/header` | `f69ca1dabe8678ff82645891ce28fbaa64cf7ecd78be4e0bb68a31db7505da6d` | Página `header` do wiki. |

## Fonte: Man7 / man-pages (seções 2/3)
| Categoria | Formato | Caminho local | Hash SHA256 | Nota |
| --- | --- | --- | --- | --- |
| SECUNDÁRIA | TAR.XZ | `data/knowledge_raw/c/man7/man-pages-6.02.tar.xz` | `66d809b62ba8681ebcbd1a8d0a0670776924ab93bfbbb54e1c31170e14303795` | Release oficial extraída para `data/knowledge_raw/c/man7/man-pages-6.02/`; manter a GPL. |

## Pending sources / documentos não congelados
| Fonte | Motivo |
| --- | --- |
| ISO/IEC 9899:2018 (C17) oficial | Norma precisa de compra/licença; por ora usamos N2610 como proxy e registrar o número da compra quando disponível. |

## Diretórios criados
- `data/knowledge_raw/c/iso_c17` (uso futuro para ISO pago)
- `data/knowledge_raw/c/wg14/`
- `data/knowledge_raw/c/posix_issue7/`
- `data/knowledge_raw/c/cppreference_c/`
- `data/knowledge_raw/c/man7/` + extração `man-pages-6.02/`

## Nota operacional
- Qualquer alteração no corpus (hash updating, novo arquivo, etc.) exige atualização deste lockfile e revalidação antes de qualquer parsing.
