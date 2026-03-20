# HANDOFF: C Domain Integration (2026-03-16T23:36:10Z)

## Contexto
- O piloto da linguagem C já passou pelas etapas de chunking controlado, validação nela e geração dos embeddings isolados em `data/semantic_index_experiments/c_pilot/`.
- A rodada atual promove o piloto para um domínio formal que permanece isolado do índice legado e possui um utilitário local de consulta.

## O que foi feito
1. Criada a estrutura `data/knowledge_domains/c_programming/{corpus,chunks,embeddings,metadata}` e copiados os artefatos chave (lock, manifesto, chunks, embeddings, metadados).
2. Documentado o domínio em `docs/C_DOMAIN_MANIFEST.md` e registrado os metadados estruturados em `data/knowledge_domains/c_programming/metadata/domain_metadata.json` e `metadata/chunk_index.json` (com campo `domain_chunk_path`).
3. Desenvolvido `scripts/c_domain_query.py`, que consome somente o vetor isolado de C e retorna os top chunks com título, seção, snippet e caminho dentro do domínio.
4. Executados os cinco testes principais (`read`, `pthread_create`, `assert`, `printf`, `comportamento definido pela implementação`), registrando os chunks, fontes e avaliações dentro do relatório de integração.
5. Gerado `docs/C_DOMAIN_INTEGRATION_REPORT_20260316T233610Z.md` (detalhando consultas e lacunas) e atualizado `STATUS.md` com o checkpoint desta etapa.

## Próximos passos recomendados
1. Reforçar o chunk `<assert.h>` (ou sinalizar o man7) para que o embedding semântico não volte a cair no placeholder minimalista.
2. Rerodar a bateria semântica localizada assim que o `<assert.h>` melhorar e verificar se `assert` e `<assert.h>` passam a usar o chunk `man7/assert.3` em primeiro lugar.
3. Após a estabilização, tocar a integração com o índice global (ex: pipeline de ingestão condicional) mantendo o domínio isolado até que não haja regressões no ranking geral.
