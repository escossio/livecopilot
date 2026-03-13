# Checklist Canonico de Fechamento de Rodada Semantica

## Objetivo
Padronizar o fechamento de rodadas semanticas sem alterar o pipeline funcional.

## Escopo
- Processo manual e auditavel.
- Sem hook automatico no pipeline.
- Aplicavel a rodadas de ingestao + persistencia + auditoria por dominio.

## Checklist obrigatorio
1. Validar ingestao canonica da rodada:
   - confirmar `documents_processed`, `documents_ignored`, `parsing_errors`.
   - confirmar parsed/chunks do recorte em `data/knowledge_parsed/` e `data/knowledge_chunks/`.
2. Validar persistencia semantica do recorte:
   - registrar `documents_selected`, `documents_processed`, `documents_validated`, `documents_failed`, `chunks_persisted`.
   - confirmar escopo restrito por `source_file`/filtro da rodada.
3. Executar auditoria semantica before/after (mesma bateria de perguntas):
   - registrar `well`, `partial`, `gap`, `avg_max`, `avg_avg`.
   - registrar delta e mudanca de classe por pergunta.
4. Executar scanner UTF-8 (obrigatorio no fechamento processual):
   - comando padrao:
```bash
scripts/utf8_hygiene_scan.sh \
  --output docs/coverage/utf8_hygiene_scan_validation_<YYYYMMDD>_<rodada>.json \
  --pretty
```
   - aprovacao:
     - `bad_chunks_count == 0`
     - `affected_source_files_count == 0`
   - reprovacao:
     - qualquer valor `> 0` em `bad_chunks_count`.
     - acao minima: registrar artefato + evidencias no `STATUS.md` e abrir rodada curta separada de higiene (sem alterar pipeline principal nesta rodada).
5. Consolidar artefatos da rodada em `docs/coverage/` e listar no checkpoint.
6. Atualizar `STATUS.md` com:
   - hipotese da rodada
   - execucao realizada
   - evidencias objetivas
   - limitacoes atuais
   - proximo passo recomendado
7. Criar handoff curto em `docs/HANDOFF_*_<YYYYMMDD>.md` com resumo auditavel.

## Template curto de fechamento
```markdown
# Handoff - <rodada> (<YYYY-MM-DD>)

## Escopo
- Dominio/recorte:
- Fonte oficial:

## Validacoes
- Ingestao:
- Persistencia semantica:
- Auditoria before/after:
- UTF-8 hygiene scan:

## Aprovacao de fechamento
- Resultado: aprovado | reprovado
- Motivo objetivo:

## Artefatos
- docs/coverage/<...>.json
- docs/HANDOFF_<...>.md
- STATUS.md
```

## Observacao
Este checklist adiciona disciplina operacional de fechamento. Ele nao substitui nem altera os scripts canonicos de ingestao/persistencia.
