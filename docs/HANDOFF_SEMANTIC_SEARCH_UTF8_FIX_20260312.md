# Handoff - UTF8 Fix no semantic_search (2026-03-12)

## Objetivo
Remover bloqueio por erro UTF-8 no caminho padrão de `semantic_search` com correção mínima, sem alterar pipeline.

## Causa raiz confirmada
- Erro reproduzido no `semantic_search`:
  - `psycopg.errors.CharacterNotInRepertoire: sequência de bytes é inválida para codificação "UTF8": 0xe2 0x94`
- Evidência técnica:
  - `docs/coverage/semantic_search_utf8_diagnostic_20260312.json`
  - `server/client encoding = UTF8`
  - falha ocorre ao ler snippet de `chunks.content` (`LEFT(c.content, 180)`).
  - mesma busca sem ler `content` (snippet por `title`) funciona.

## Correção aplicada (mínima e segura)
- Arquivo alterado: `app/services/semantic_min_api.py`
- Estratégia:
  1. manter busca normal com snippet de `content`.
  2. em `CharacterNotInRepertoire`, usar `SAVEPOINT` + `ROLLBACK TO SAVEPOINT` e rerodar a mesma query com snippet de `title`.
  3. expor flags no retorno/cache:
     - `snippet_fallback_due_encoding`
     - `snippet_fallback_error`
- Resultado: busca semântica volta a responder sem exceção, preservando ranking vetorial.

## Validação
- `semantic_search` executa no caminho padrão sem exception.
- `knowledge_gap_engine` rerodado sem fallback histórico (0 linhas por domínio):
  - `docs/coverage/knowledge_gap_engine_validation_post_utf8_fix_20260312.json`
- Consolidação da validação:
  - `docs/coverage/semantic_search_utf8_fix_validation_20260312.json`

## Limitação residual
- Há registros legados com bytes inválidos em `chunks.content`; o fallback de snippet continua ativo quando esse dado é atingido.

## Próximo passo recomendado
- Rodada de higiene focada em `chunks.content` legado para reduzir/eliminar fallback de snippet, sem alterar contrato do pipeline.
