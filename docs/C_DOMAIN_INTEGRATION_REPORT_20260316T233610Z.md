# Relatório de Integração do Domínio C — 2026-03-16T23:36:10Z

## Estrutura do domínio
- `data/knowledge_domains/c_programming/` agora sacramenta o piloto C, com subdiretórios `corpus/`, `chunks/`, `embeddings/` e `metadata/`.
- O corpus congelado (`C_CORPUS_LOCK.md`/`.json`) e o manifesto original (`C_SOURCE_MANIFEST.md`/`.json`) residem em `corpus/`, enquanto os chunks completos foram copiados para `chunks/` com a mesma organização por família.
- O índice semântico isolado (25 embeddings + metadata) vive em `embeddings/` e alimenta o utilitário de consulta `scripts/c_domain_query.py`.
- Metadados próprios guardam o inventário dos chunks (`metadata/chunk_index.json`, agora com campo `domain_chunk_path`) e o status do domínio (`metadata/domain_metadata.json`).

## Artefatos promovidos do sandbox
1. **Corpus lock / manifesto**: cópias fechadas em `data/knowledge_domains/c_programming/corpus/`, preservando as mesmas fontes e hashes validados anteriormente.
2. **Chunks**: diretório completo `data/knowledge_domains/c_programming/chunks/` replicando o subset `(wg14, posix_issue7, cppreference_c, man7)` utilizado pelo piloto.
3. **Embeddings & metadata**: `embeddings.jsonl` + `metadata.json`, agora dentro de `data/knowledge_domains/c_programming/embeddings/`.
4. **Indices auxiliares**: `metadata/chunk_index.json` (com `domain_chunk_path`) e `metadata/domain_metadata.json` descrevendo a versão 20260316T020200Z.
5. **Utilitário de consulta**: `scripts/c_domain_query.py`, que dispara queries com `text-embedding-3-large` contra esse domínio isolado.

## Consulta local ao domínio C
1. Carregue a chave em ambiente: `set -o allexport; source codex-supervisor/.env.secrets; set +o allexport`.
2. Execute `python3 scripts/c_domain_query.py "<pergunta>" --top 3` para receber os três chunks mais próximos, mostrando fonte, título, seção e snippet.
3. O script não toca no índice global e usa apenas os embeddings dentro de `data/knowledge_domains/c_programming/embeddings/`.

## Perguntas validadas e resultados
| Pergunta | Top chunk | Fonte | Título / Seção | Snippet | Avaliação |
| --- | --- | --- | --- | --- | --- |
| O que read faz em C? | `cppreference_c-08` | `cppreference_c/header.txt` | `<ctype.h>` / header entry | `<ctype.h>` | Semântico ainda posiciona o chunk `<ctype.h>` na primeira posição, embora o chunk `posix_issue7-05` (read) apareça em segundo lugar; o domínio continha o material correto, mas a ordenação pode confundir o ranking. |
| O que pthread_create faz? | `posix_issue7-04` | `posix_issue7/pthread_create.txt` | `pthread_create` / function | Explica como `pthread_create` cria threads com atributos/retornos | Excelente: o chunk dedicado é o maior score (0.566) e descreve claramente o comportamento. |
| O que assert faz? | `cppreference_c-06` | `cppreference_c/header.txt` | `<assert.h>` / header entry | `<assert.h>` | Parcial: o cabeçalho minimalista domina o ranking semântico; o chunk `man7/assert.3` surge em segundo lugar, mas o domínio precisa reforçar o conteúdo do `<assert.h>` para evitar regressões. |
| O que printf retorna? | `man7-04` | `man7/printf-3.txt` | `printf(3) RETURN VALUE` / RETURN VALUE | Descreve o número de caracteres retornado e indicação de truncamento | Muito bom: a resposta valoriza o documento oficial `printf(3)` e aparece em primeiro lugar. |
| O que é comportamento definido pela implementação em C? | `wg14-01` | `wg14/n2756.txt` | `1. INTRODUCTION` / section | Define as diversas interpretações da norma e a motivação do Concrete Memory Model | Excelente: captura a seção introdutória do WG14, fornecendo o contexto normativo desejado. |

## Execução dos testes
1. `bash -lc 'set -o allexport; source codex-supervisor/.env.secrets; set +o allexport; python3 scripts/c_domain_query.py "O que read faz em C?" --top 3'`
2. `bash -lc 'set -o allexport; source codex-supervisor/.env.secrets; set +o allexport; python3 scripts/c_domain_query.py "O que pthread_create faz?" --top 3'`
3. `bash -lc 'set -o allexport; source codex-supervisor/.env.secrets; set +o allexport; python3 scripts/c_domain_query.py "O que assert faz?" --top 3'`
4. `bash -lc 'set -o allexport; source codex-supervisor/.env.secrets; set +o allexport; python3 scripts/c_domain_query.py "O que printf retorna?" --top 3'`
5. `bash -lc 'set -o allexport; source codex-supervisor/.env.secrets; set +o allexport; python3 scripts/c_domain_query.py "O que é comportamento definido pela implementação em C?" --top 3'`

## Lacunas e próximos passos
- Enriquecer `data/knowledge_domains/c_programming/chunks/cppreference_c/cppreference_c-06.txt` (ou condicionar o embedding) para que `<assert.h>` seja verdadeiramente explicativo e evite que o domínio continue priorizando um chunk sem texto.
- Após a melhoria do `<assert.h>`, rerodar os testes da bateria semântica para confirmar que `assert`/`<assert.h>` passam a devolver o chunk `man7/assert.3` e que nenhuma outra pergunta foi impactada.
