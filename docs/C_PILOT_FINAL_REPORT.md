# Relatório Final do Piloto C — 2026-03-17T18:00:00Z

## Objetivo original
- validar um pipeline oficial-first para a linguagem C sem contaminar o índice global do LiveCopilot.
- manter o subset piloto (corpus, chunks, embeddings e metadados) isolado em `data/knowledge_domains/c_programming`.
- fornecer uma base consultável localmente e pronta para ser promovida caso o experimento se mostrasse estável.

## Hipótese testada
- Seguindo o contrato oficial-first, era possível construir um domínio C útil e estável apenas com materiais confiáveis (WG14, POSIX, cppreference, man7) e um utilitário local, preservando o índice legado.

## Método executado
1. Estruturação do domínio C isolado (corpus, chunks, embeddings, metadata) e criação de manifestos + handoff básico (**docs/C_DOMAIN_MANIFEST.md**, **docs/C_DOMAIN_INTEGRATION_REPORT_20260316T233610Z.md**).
2. Implementação do utilitário `scripts/c_domain_query.py` para consultar exclusivamente os embeddings do domínio C.
3. Refinamentos sucessivos para corrigir os pontos fracos identificados: `<assert.h>/assert` e `read()` foram enriquecidos, os embeddings foram regenerados e a bateria curta de perguntas foi rerodada com documentação detalhada em **docs/C_ASSERT_REFINEMENT_REPORT_20260317T001800Z.md** e **docs/C_READ_REFINEMENT_REPORT_20260317T013200Z.md**.

## Resultados obtidos
- Domínio `c_programming` existe formalmente com corpus congelado, chunks auditados e embeddings isolados que alimentam `scripts/c_domain_query.py`.
- O método official-first foi validado: todas as fontes são oficiais (WG14, POSIX, man7, cppreference) e a ingestão nunca tocou o índice global.
- O pipeline completo (congelamento, chunking, metadata + embeddings + consulta) foi executado sucessivamente e comprovadamente opera apenas dentro do domínio C.
- `<assert.h>/assert`, `read()`, `printf`, `pthread_create` e `behavior defined by implementation` agora são respondidos pelos chunks esperados e documentados nos relatórios e arquivos de resultados indicados acima.
- Mantivemos o índice legado intacto, pois todo o trabalho foi realizado no domínio isolado e o utilitário local nunca acessa outros índices.

## Problemas encontrados
- O chunk de `<assert.h>` originalmente era minimalista (cppreference) e dominava o ranking, deixando o `man7/assert.3` em segundo lugar.
- O chunk de `read()` era semântico insuficiente; o ranking promovia `<ctype.h>` como resposta para a pergunta.
- Além disso, o domínio precisava de um registro final e institucional do experimento aberto no `PROJECT_BRAIN` e no STATUS.

## Correções aplicadas
- Substituição/enriquecimento do chunk `<assert.h>` com conteúdo completo sobre a macro `assert`, `NDEBUG`, `abort` e casos de uso (documentado em **docs/C_ASSERT_REFINEMENT_REPORT_20260317T001800Z.md** com resultados em **docs/C_ASSERT_REFINEMENT_RESULTS_20260317T001800Z.json**).
- Reforço do chunk de `read()` com assinatura, comportamentos e valores de retorno, seguido de regeneração de embeddings e rerun da bateria curta (**docs/C_READ_REFINEMENT_REPORT_20260317T013200Z.md** e **docs/C_READ_REFINEMENT_RESULTS_20260317T013200Z.json**).
- Atualização continuada dos metadados do domínio, mantendo versão e inventário alinhados com as ações aplicadas.

## Estado final do domínio C
- Estrutura completa em `data/knowledge_domains/c_programming/`, com corpus limitado ao piloto aprovado e metadados consistentes.
- Query local pronta em `scripts/c_domain_query.py` e validada com as perguntas-chaves da bateria.
- Embeddings, chunks e corpus intactos e não alterados nesta rodada de encerramento.

## O que foi provado
- O método official-first é viável para construir domínios isolados e consultáveis sem tocar o índice global.
- O pipeline completo (congelamento, chunking, embeddings, metadata e consulta local) pode ser validado em ciclos curtos como o do piloto C.
- O domínio C isolado está operacional e pronto para ser mantido, promovido ou replicado.
- O índice global permanece preservado porque apenas o domínio isolado foi manipulado.

## Limitações remanescentes
- O domínio ainda responde a um conjunto limitado de perguntas aprovadas; qualquer expansão exige nova rodada controlada.
- O reforço semântico deve ser monitorado para evitar placeholders em novos tópicos (por exemplo, outros cabeçalhos normativos além de `<assert.h>`).

## Resultado final do experimento
O piloto C foi concluído: oficialmente validamos o método official-first, o domínio isolado opera com consulta local e o índice global permanece preservado; o experimento é considerado encerrado, com o domínio pronto para manutenção ou promoção controlada.
