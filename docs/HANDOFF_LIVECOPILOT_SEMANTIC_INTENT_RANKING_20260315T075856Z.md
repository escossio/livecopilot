# HANDOFF LIVECOPILOT SEMANTIC INTENT RANKING

## Motivação
- os casos ainda `PARCIALMENTE COERENTE` apontavam claramente para chunks semânticos desalinhados com a intenção da pergunta, mesmo que o documento correto fosse escolhido.
- o objetivo era validar essa hipótese, aplicar o ajuste mínimo de ranking por intenção e mensurar o impacto sem arrancar o pipeline que já está estável.

## Diagnóstico
- o `diagnostic trace` levantado em `docs/diagnostics/semantic_intent_ranking_diagnostic_20260315T075619Z.md` mostra que 9 dos 10 casos do subset estavam usando front matters ou definições quando a intenção pedia definição/finalidade/uso.
- o artefato `docs/diagnostics/semantic_intent_chunk_trace_20260315T075619Z.json` guarda os snippets top e os tipos detectados.

## Ajuste aplicado
- `app/services/knowledge_search.py` agora detecta a intenção (`what_is`, `purpose`, `when_to_use`, `difference`, `how`) e classifica semanticamente cada chunk como `definition`, `purpose`, `use`, `difference`, `mechanism`, `noise` ou `other`.
- um bônus leve (`INTENT_ALIGNMENT_BONUS = 0.09`) é somado ao score quando o chunk_type casa com a intenção detectada, mantendo intactos os demais pesos de lexicografia, estrutura e praticidade.
- os resultados mais baixos continuam disponíveis como fallback estrutural; o bônus só afeta a ordenação quando há candidatos alinhados.

## Resultados
- o subset de 10 perguntas ainda não gerou respostas COERENTES (todos PARCIALMENTE COERENTES, conforme `docs/validation/semantic_intent_ranking_subset_20260315T075823Z.json`), mas o relatório `semantic_intent_ranking_subset_report_20260315T075823Z.md` documenta que a camada serve para evitar regressões e preparar tubulações futuras.
- a baseline ampliada rerodada (`docs/validation/semantic_regression_expanded_post_intent_ranking_20260315T075856Z.json`) manteve exatamente os mesmos totais por domínio, sem regressão nem ganho imediato.

## Próximos passos
- refinar os filtros de preparação do chunk (por exemplo removendo front matters ou promovendo chunks alternativos) para que o bônus semântico tenha candidatos alinhados e possa converter parciais em coerentes.
