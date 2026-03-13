# HANDOFF - Composed Rule Simulation (20260312T180937Z)

## Status final
- Simulacao de regra composta concluida.
- Nenhuma mudanca aplicada na classificacao real de producao.

## O que foi executado
1. Consolidacao de sinais por query em 5 dominios (44 queries).
2. Simulacao de 3 regras compostas minimas (A/B/C).
3. Comparacao de impacto por regra e por dominio contra baseline.
4. Decisao de viabilidade para prototipo.
5. Fechamento UTF-8.

## Regra candidata
- Selecionada: `rule_C_max055_avg050_official`
- Definicao: well se baseline OU (`max>=0.55` e `avg>=0.50` e `top1_expected_official`).
- Impacto:
  - Terraform: `partial->well +2`
  - Nao-Terraform: `partial->well +0`
  - Regressao well->partial: `0`

## Artefatos
- `docs/coverage/composed_rule_signals_consolidated_20260312T180937Z.json`
- `docs/coverage/composed_rule_simulation_20260312T180937Z.json`
- `docs/coverage/composed_rule_decision_20260312T180937Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_composed_rule_closeout.json`

## Decisao
- `regra_composta_minima_merece_prototipo`
- Recomendacao: prototipar em branch experimental/offline com guardrails cross-domain; nao promover direto.

## UTF-8
- `total_chunks_scanned=1243`
- `bad_chunks_count=0`
- `affected_source_files_count=0`
