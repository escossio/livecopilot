# UTF8 Hygiene Scanner

Scanner read-only para detectar regressão de encoding em `chunks.content` no probe de snippet (`LEFT(content, 180)`).

## Uso
```bash
scripts/utf8_hygiene_scan.sh --pretty
```

Salvar artefato JSON:
```bash
scripts/utf8_hygiene_scan.sh \
  --max-affected-rows 500 \
  --output docs/coverage/utf8_hygiene_scan_validation_20260312.json \
  --pretty
```

## Campos principais da saída
- `generated_at`
- `bad_chunks_count`
- `affected_source_files_count`
- `affected_rows`
- `grouped_by_source_file`
- `affected_rows_returned`
- `affected_rows_truncated`

## Observações
- O scanner não persiste alterações no banco (`read_only=true` no relatório).
- Se `bad_chunks_count > 0`, a rodada deve registrar evidência e decidir correção em ciclo separado.
