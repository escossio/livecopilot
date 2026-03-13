# Handoff - Scanner Read-only de Higiene UTF-8 (2026-03-12)

## Objetivo
Automatizar a deteccao de regressao de encoding UTF-8 em `chunks.content` sem alterar pipeline e sem corrigir dados nesta rodada.

## Implementacao
- Script principal: `scripts/utf8_hygiene_scan.py`
- Wrapper: `scripts/utf8_hygiene_scan.sh`
- Documentacao: `docs/UTF8_HYGIENE_SCANNER.md`

## Regra de deteccao
- Probe por chunk no caminho que historicamente quebrava:
  - `LEFT(content, 180)`
- Captura de `CharacterNotInRepertoire` com `SAVEPOINT`/`ROLLBACK TO SAVEPOINT`.
- Execucao em transacao com `rollback` final (read-only operacional).

## Saida JSON
- `generated_at`
- `scanner`
- `read_only`
- `snippet_probe_sql`
- `total_chunks_scanned`
- `bad_chunks_count`
- `affected_source_files_count`
- `affected_rows`
- `affected_rows_returned`
- `affected_rows_truncated`
- `grouped_by_source_file`

## Validacao da rodada
- Comando:
```bash
scripts/utf8_hygiene_scan.sh --pretty --output docs/coverage/utf8_hygiene_scan_validation_20260312.json
```
- Resultado atual:
  - `bad_chunks_count=0`
  - `affected_source_files_count=0`
  - `total_chunks_scanned=845`
- Artefato:
  - `docs/coverage/utf8_hygiene_scan_validation_20260312.json`

## Limitacoes atuais
- Scanner ainda e execucao manual (nao hook obrigatorio).
- Cobre regressao no probe de snippet; nao substitui higiene profunda de todo payload textual.

## Proximo passo recomendado
- Incluir esse scanner no checklist de fechamento de rodada semantica (passo padrao opcional), sem alterar pipeline principal.
