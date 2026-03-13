# HANDOFF - Terraform Threshold Diagnosis (20260312T174039Z)

## Status final
- Rodada de diagnostico de classificacao semantica concluida.
- Objetivo atingido: validar se o `partial` residual vem de threshold rigido ou de residual legitimo.

## O que foi executado
1. Extracao dos scores (`max/avg`) por query da bateria Terraform round2 after.
2. Calculo de distancia aos thresholds atuais.
3. Distribuicao estatistica (`min/max/mean/p50/p75/p90`) para `max_score` e `avg_score`.
4. Simulacao de cenarios de recalibracao (`well_max`: 0.59, 0.58, 0.57, 0.56, 0.55, 0.54).
5. Decisao objetiva de calibracao.
6. Fechamento UTF-8.

## Thresholds atuais
- `gap_if_max_below=0.45`
- `well_covered_if_max_at_least=0.60`
- `well_covered_requires_avg_at_least=0.45`

## Resultado principal
- Gargalo observado: `max_score`, nao `avg_score`.
- Distancia media ate `well_max`:
  - `avg_distance_to_well_max=0.016099`
- Distancia media ate `well_avg`:
  - `avg_distance_to_well_avg=-0.107130` (ou seja, avg ja sobra).

## Simulacao e decisao
- Em `well_max=0.59/0.58/0.57/0.56`: nenhuma conversao `partial -> well`.
- Primeira conversao sem regressao so em `well_max=0.55`.
- Decisao: `threshold_correto_partial_legitimo`.
- Justificativa: para converter classes seria necessario afrouxamento agressivo (`well_max<=0.55`), inadequado para criterio geral sem validacao multi-dominio.

## Artefatos
- `docs/coverage/terraform_threshold_diagnosis_scores_20260312T174039Z.json`
- `docs/coverage/terraform_threshold_diagnosis_distribution_20260312T174039Z.json`
- `docs/coverage/terraform_threshold_diagnosis_simulation_20260312T174039Z.json`
- `docs/coverage/terraform_threshold_diagnosis_report_20260312T174039Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_threshold_round_closeout.json`

## UTF-8 closeout
- `total_chunks_scanned=1243`
- `bad_chunks_count=0`
- `affected_source_files_count=0`

## Proximo passo recomendado
- Nao recalibrar threshold global agora.
- Executar rodada micro-targeted de recall/queryset nas 3 queries ainda `partial`.
