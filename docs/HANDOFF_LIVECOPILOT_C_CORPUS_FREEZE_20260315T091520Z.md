# HANDOFF: C Corpus Freeze

## Contexto
- Continuação do manifesto (`docs/C_SOURCE_MANIFEST.md` / `.json`) e do handoff anterior de manifesto (`docs/HANDOFF_LIVECOPILOT_C_SOURCE_MANIFEST_20260315T090500Z.md`).
- Objetivo desta rodada: congelar localmente as fontes aprovadas, registrar hashes, e gerar o lockfile antes de partir para parsing.

## Corpus bruto congelado
- Diretórios criados sob `data/knowledge_raw/c/`:
  - `iso_c17/` (para o PDF oficial quando disponível)
  - `wg14/` (contendo `n2610.pdf` e `n2756.pdf`)
  - `posix_issue7/` (páginas HTML de stdio.h, stdlib.h, pthread.h, unistd.h, printf, pthread_create, read, exit)
  - `cppreference_c/` (páginas `language` e `header` baixadas via `wget`)
  - `man7/` (release `man-pages-6.02.tar.xz` extraída para `man-pages-6.02/`)
- Lockfile: `docs/C_CORPUS_LOCK.md` + `docs/C_CORPUS_LOCK.json` documentam caminhos, hashes e notas.

## Pendências
- ISO/IEC 9899:2018 oficial ainda não foi comprado; manter rastreamento da compra/licença e atualizar `docs/C_CORPUS_LOCK.*` assim que o PDF oficial estiver no diretório `data/knowledge_raw/c/iso_c17/`.

## Próximo passo recomendado
- Validar os arquivos baixados (hash, presença) e só depois iniciar parsing/chunking em lotes, conforme o manifesto. Garantir que o lockfile esteja versionado antes de qualquer ingestão automática.
