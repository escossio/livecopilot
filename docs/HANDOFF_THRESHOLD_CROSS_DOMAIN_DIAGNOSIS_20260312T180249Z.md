# HANDOFF - Threshold Cross-Domain Diagnosis (20260312T180249Z)

## Status final
- Rodada de simulacao cross-domain concluida.
- Nenhuma alteracao de threshold real foi aplicada.

## Escopo executado
1. Coleta comparavel por query dos dominios: `aws_iam`, `docker`, `terraform`, `observability`, `kubernetes`.
2. Simulacao de `well_max` em `0.60..0.54` (mantendo `gap=0.45` e `avg_well=0.45`).
3. Analise de impacto por dominio e global.
4. Simulacao analitica de regra composta minima.
5. Decisao objetiva com recomendacao.
6. Fechamento UTF-8.

## Resultado principal
- Terraform so comeca a converter `partial->well` em `well_max=0.55`.
- Nesse ponto, ha inflacao nos outros dominios maior que o ganho em Terraform (`+3` nao-TF vs `+2` TF).
- Regra composta minima testada (`max>=0.60 OR max>=0.57 + top1 oficial`) nao converteu Terraform e converteu 1 query fora de Terraform.
- Decisao: **manter threshold global atual (`well_max=0.60`)** nesta etapa.

## Artefatos
- `docs/coverage/threshold_cross_domain_query_consolidated_20260312T180249Z.json`
- `docs/coverage/threshold_cross_domain_simulation_20260312T180249Z.json`
- `docs/coverage/threshold_cross_domain_composed_rule_simulation_20260312T180249Z.json`
- `docs/coverage/threshold_cross_domain_decision_20260312T180249Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_threshold_cross_domain_closeout.json`

## UTF-8
- `total_chunks_scanned=1243`
- `bad_chunks_count=0`
- `affected_source_files_count=0`

## Proximo passo recomendado
- Manter threshold global e atacar residual via micro-round de recall/queryset em Terraform; depois revalidar cross-domain com a mesma metodologia.
