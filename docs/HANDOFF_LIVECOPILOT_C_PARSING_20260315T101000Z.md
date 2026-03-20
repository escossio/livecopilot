# HANDOFF: C Parsing Phase

## Contexto
- Continuação do lockfile e manifesto congelados (`docs/C_CORPUS_LOCK.*`, `docs/C_SOURCE_MANIFEST.*`).
- Objetivo: criar o corpus parseado em `data/knowledge_parsed/c/` e formalizar a política/amostras antes de qualquer chunking.

## Política aplicada
- `docs/C_PARSING_POLICY.md` descreve as regras por tipo: `pdftotext` para WG14, BeautifulSoup para HTML (POSIX/cppreference) e `groff -mandoc` para man-pages.
- O processo remove navegadores, front matter e metadata, preservando títulos, descrições e exemplos técnicos.

## Corpus parseado gerado
- Diretórios: `data/knowledge_parsed/c/{wg14,posix_issue7,cppreference_c,man7}`.
- Parsing: textos salvos em `.txt`; cada HTML e PDF agora tem versão limpa e legível.
- Lockfile mantido congelado; qualquer alteração requer atualização e reparseamento.

## Amostras antes/depois
- `docs/C_PARSING_SAMPLE_REPORT_20260315T100200Z.md` compara `n2610.pdf` → `n2610.txt`, `stdio.h.html` → `stdio.h.txt`, `cppreference language/header`, `man3/printf.3` → `printf-3.txt`.
- Avaliação aponta quais ruídos foram removidos e que o parseado está pronto para chunking posterior.

## Próximos passos
- Validar o corpus parseado (hashes) e iniciar o chunking (lote 1) seguindo os lotes do manifesto, já com áudio de navegação eliminada.
