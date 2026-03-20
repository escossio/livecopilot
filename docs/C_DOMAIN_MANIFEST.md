# C Domain Manifest

## Nome do domínio
**C Programming Pilot Domain** — um domínio isolado da linguagem C dentro do projeto LiveCopilot.

## Objetivo
Manter o subset piloto validado de chunks, embeddings e metadados de C em uma estrutura dedicada, permitindo consultas locais (sem misturar com o índice global) e preparando o domínio para futuras integrações controladas.

## Origem do corpus
O corpus foi congelado conforme `docs/C_CORPUS_LOCK.md`/`.json`, capturando os hashes e fontes oficiais (WG14, POSIX Issue 7, cppreference, man7) listadas em `docs/C_SOURCE_MANIFEST.md`.

## Fontes usadas
- **WG14 (N2610/N2756)**: base normativa do comité ISO/IEC 9899 com foco em comportamentos definidos pela implementação.
- **The Open Group Base Specifications Issue 7**: capítulos críticos de `<stdio.h>`, `<pthread.h>`, `<unistd.h>` e exemplos de syscalls (read, printf, pthread_create).
- **cppreference (linguagem + headers)**: visão didática dos blocos de linguagem e cabeçalhos (`<assert.h>`, `<ctype.h>`, etc.).
- **Man7 – man-pages**: troff convertido em texto para `printf(3)`, `locale(7)` e `assert(3)`.

## Estado atual do piloto
- 25 chunks aprovados, cada um com `.txt` + `.meta.json`, organizados por família e auditados em `docs/C_CHUNKING_METADATA.json`.
- Embeddings isolados gerados via `text-embedding-3-large` e guardados em `data/knowledge_domains/c_programming/embeddings/` (embeddings.jsonl + metadata.json).
- Metadata de domínio atualizada em `data/knowledge_domains/c_programming/metadata/domain_metadata.json` com sinal de versão `20260316T020200Z`.
- Query local disponível via `scripts/c_domain_query.py` e validada com a bateria semântica mínima definida no baseline.

## Limitações conhecidas
1. A busca semântica ainda prefere o placeholder `cppreference_c/<assert.h>` para perguntas sobre `assert`, o que indica que o chunk do cabeçalho precisa de conteúdo real ou sinal reforçado.
2. O domínio atual não expõe diretamente o corpus bruto ou o índice global: continua isolado e deve ser consultado pelo utilitário local.

## Perguntas que o domínio responde bem
- **O que read faz em C?** → `data/knowledge_domains/c_programming/chunks/posix_issue7/posix_issue7-05.txt`
- **O que pthread_create faz?** → `data/knowledge_domains/c_programming/chunks/posix_issue7/posix_issue7-04.txt`
- **O que printf retorna?** → `data/knowledge_domains/c_programming/chunks/man7/man7-04.txt`
- **O que é comportamento definido pela implementação em C?** → `data/knowledge_domains/c_programming/chunks/wg14/wg14-01.txt`
- **O que é locale em C?** → `data/knowledge_domains/c_programming/chunks/man7/man7-05.txt` e `locale.7` overview.

## Lacunas restantes
- **O que é <assert.h>?** e **Para que serve assert?** mantêm dupla resposta: a camada lexical usa `man7/assert.3`, mas a semântica ainda recai no chunk mínimo de cppreference. Sem reforço no embedding do `<assert.h>`, o domínio continuará preferindo o placeholder e poderá causar regressões.
- A cobertura além dos nove tópicos validados (stdout, sockets, threading, locale/behavior) ainda não foi testada; qualquer nova pergunta exigirá extensão controlada do corpus.
