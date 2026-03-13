# HANDOFF - Prefix Ingest Hardening (20260312T193121Z)

## Status final
- Hardening minimo do modo `--source-prefix` concluido.
- Compatibilidade preservada.
- Persistencia semantica nao alterada.

## O que mudou
- `app/services/knowledge_ingest.py`
  - validacao de prefixo:
    - rejeita vazio apos normalizacao
    - rejeita `..` (path traversal)
  - novo flag:
    - `--strict-source-prefix`
  - saida de troubleshooting:
    - prefixos normalizados
    - contagem por prefixo
  - falhas de validacao com mensagem limpa (`Erro: ...`) e exit code `2`.

- `docs/INGESTION_SELECTIVE_PREFIX_MODE.md`
  - documentado `--strict-source-prefix`
  - validacoes e erros esperados.

## Validacao executada
- Consolidado:
  - `docs/coverage/prefix_ingest_hardening_validation_20260312T192630Z.json`
- Resumo:
  - valido unico: PASS (`found=12`)
  - valido multiplo: PASS (`found=23`)
  - inexistente sem strict: PASS (`found=0`, sem falha)
  - inexistente com strict: PASS (falha controlada, `exit=2`)
  - prefixo com `..`: PASS (falha controlada, `exit=2`)

## UTF-8 closeout
- `docs/coverage/utf8_hygiene_scan_validation_prefix_ingest_hardening_closeout.json`
- `total_chunks_scanned=1282`, `bad_chunks_count=0`, `affected_source_files_count=0`

## Proximo passo recomendado
- Implementar persistencia semantica seletiva por prefixo como extensao natural do fluxo, sem perder modo legado por `source_file` explicito.
