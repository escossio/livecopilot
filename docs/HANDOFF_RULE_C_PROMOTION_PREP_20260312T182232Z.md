# HANDOFF - Rule C Promotion Prep (20260312T182232Z)

## Status final
- Preparacao para promocao controlada concluida em trilha experimental.
- Baseline de producao permanece como padrao (nenhuma troca de regra default).

## O que foi implementado
- Modulo reutilizavel experimental: `app/services/semantic_classification_experimental.py`
- Utilitario experimental preparado com modos explicitos: `scripts/composed_rule_experimental_eval.py`
  - `--mode baseline` (default)
  - `--mode rule_c` (exige ativacao)
  - `--mode compare` (exige ativacao)
  - `--mode guardrails`
- Ativacao explicita da Regra C:
  - `--enable-rule-c` OU `LIVECOPILOT_EXPERIMENTAL_RULE_C=1`
- Robustez: script agora injeta `PROJECT_ROOT` no `sys.path` para funcionar sem `PYTHONPATH` manual.

## Guardrails automatizados
- `no_well_to_partial_regressions`
- `no_non_official_promotions`
- `non_target_well_gain_cap <= 1`
- `target_domain_terraform_gain >= 1`

## Validacao (baseline vs experimental)
- Artefatos:
  - `docs/coverage/rule_c_promotion_prep_baseline_vs_rule_c_20260312T182232Z.json`
  - `docs/coverage/rule_c_promotion_prep_guardrails_20260312T182232Z.json`
  - `docs/coverage/rule_c_promotion_prep_decision_20260312T182232Z.json`
- Recheck de guardrails:
  - `docs/coverage/rule_c_promotion_prep_recheck_guardrails_20260312T182150Z.json`
  - `docs/coverage/rule_c_promotion_prep_recheck_decision_20260312T182150Z.json`
- Resultado:
  - Baseline: `well=31`, `partial=13`, `gap=0`
  - Experimental: `well=33`, `partial=11`, `gap=0`
  - Delta: `well=+2`, `partial=-2`, `gap=0`
  - Impacto por dominio: Terraform `+2`, demais `+0`
  - Guardrails: `all_pass=true`

## Decisao
- `rule_c_ready_for_promotion_preparation`
- Regra C pronta para fase seguinte de promocao controlada (PR/CI experimental), sem rollout em producao nesta rodada.

## UTF-8 closeout
- Artefato: `docs/coverage/utf8_hygiene_scan_validation_rule_c_promotion_prep_closeout.json`
- Resultado: `total_chunks_scanned=1243`, `bad_chunks_count=0`, `affected_source_files_count=0`

## Proximo passo recomendado
- Abrir PR de promocao controlada com gate CI obrigatorio para comparacao baseline vs experimental + guardrails; manter flag default off no merge inicial.
