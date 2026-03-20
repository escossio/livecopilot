# C Chunking Policy

Este documento descreve as heurísticas aplicadas ao subset piloto de chunking para o corpus oficial-first da linguagem C.

## Visão geral
- O subset usa somente o corpus parseado em `data/knowledge_parsed/c/` e produz chunks em `data/knowledge_chunks/c/` organizados por fonte (`wg14`, `posix_issue7`, `cppreference_c`, `man7`).
- Cada chunk ganhou metadados persos em `data/knowledge_chunks/c/<fonte>/<chunk_id>.meta.json`; o inventário completo está em `docs/C_CHUNKING_METADATA.json`.
- Os chunks reservam contexto suficiente (títulos, descrições, parâmetros) e dispensam navegação ou formatação residual antes de qualquer embedding.

## WG14 normativo
- O texto de `n2756.txt` foi dividido pelas linhas que combinam cabeçalhos numerados (ex.: `1. INTRODUCTION`, `2. LIMITS AND EXPECTATIONS ...`).
- Cada chunk inclui o texto entre um cabeçalho e o próximo, preservando frases completas e removendo páginas/cabeçalhos repetidos via limpeza de espaços.
- Limitamos o subset aos primeiros cinco trechos (introdução, limitações, small storage, type punning, etc.) para manter o lote controlado.

## POSIX / The Open Group
- As páginas HTML de `stdio.h`, `stdlib.h`, `pthread.h`, `pthread_create` e `read` foram limpas com BeautifulSoup e convertidas para texto plano.
- Cada chunk corresponde a um desses arquivos, contendo o NAME/SYNOPSIS/DESCRIPTION e notas, mas sem menus, cabeçalhos ou rodapés.
- Os chunks mantêm o cabeçalho original do item (ex.: `printf`, `pthread_create`) como tópico.

## Cppreference — linguagem
- O corpo de `c/language` foi dividido pelos principais blocos do índice (Basic concepts, Keywords, Preprocessor, Statements, Expressions).
- Cada chunk agrupa a lista de conceitos seguintes a um bloco, removendo elementos de navegação ([edit], navbar) e mantendo o universo conceitual.
- O chunking está limitado às cinco primeiras seções para evitar explodir o subset.

## Cppreference — headers
- A tabela de headers (assert.h, complex.h, etc.) foi convertida em texto e os cinco primeiros cabeçalhos viraram chunks.
- Cada chunk junta a linha `<name.h>` com sua descrição e notas de versão, sem legendas de edição.

## Man-pages (man7)
- O troff `printf.3` foi convertido em texto plano (`groff -mandoc`) e os blocos NAME/SYNOPSIS/DESCRIPTION/RETURN VALUE/ERRORS viraram chunks separados.
- Escape sequences ANSI foram removidas antes do chunking para manter apenas frases e listas claras.

## Manifestos e registros
- O manifesto oficial `docs/C_SOURCE_MANIFEST.md` + `docs/C_SOURCE_MANIFEST.json` ainda guia os lotes.
- O estado congelado com hashes está em `docs/C_CORPUS_LOCK.*`.
- O inventário de chunks e metadados resumidos está em `docs/C_CHUNKING_METADATA.json` (adicionado nesta rodada).
