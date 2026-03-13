# HANDOFF - Rule C Experimental Round (20260312T181537Z)

## Status final
- Prototipo experimental/offline da Regra C implementado e executado.
- Nenhuma alteracao na regra de producao.

## Implementacao
- Script novo: `scripts/composed_rule_experimental_eval.py`
- Entradas:
  - sinais consolidados cross-domain (`composed_rule_signals_consolidated_20260312T180937Z.json`)
- Saidas:
  - `rule_c_experimental_baseline_vs_rule_c_20260312T181537Z.json`
  - `rule_c_experimental_guardrails_20260312T181537Z.json`
  - `rule_c_experimental_decision_20260312T181537Z.json`

## Resultado
- Baseline: `well=31`, `partial=13`, `gap=0`
- Regra C experimental: `well=33`, `partial=11`, `gap=0`
- Delta: `well=+2`, `partial=-2`

## Impacto por dominio
- Terraform: `+2` well (partial->well)
- Aws_IAM/Docker/Observability/Kubernetes: `+0`
- Regressao well->partial: `0`

## Guardrails
- `no_well_to_partial_regressions`: PASS
- `no_non_official_promotions`: PASS
- `non_target_well_gain_cap <=1`: PASS
- `target_domain_terraform_gain >=1`: PASS
- `all_pass=true`

## Decisao
- `rule_c_ready_for_promotion_preparation`
- Recomendacao: preparar promocao futura com validacao ampliada (ainda sem rollout).

## UTF-8 closeout
- `total_chunks_scanned=1243`
- `bad_chunks_count=0`
- `affected_source_files_count=0`

## Proximo passo recomendado
- Abrir PR de preparacao da Regra C sob modo experimental/flag, com bateria cross-domain ampliada e guardrails automatizados no pipeline de avaliacao.
