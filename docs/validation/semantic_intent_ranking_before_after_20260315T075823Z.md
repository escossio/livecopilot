# Semantic intent ranking before/after (20260315T075823Z)

- **Antes:** as 10 perguntas parciais escolhiam snippets com metadata ou definições desalinhadas à intenção, o que contaminava a síntese final. O subset listado em `semantic_llm_summary_subset_20260315T074701Z.json` evidencia esse comportamento.
- **Depois:** o ranking agora considera o tipo semântico do chunk e privilegia o tipo esperado para cada intenção (`definition` para `o que é`, `purpose` para `para que serve`, `use` para `quando usar`). Apesar disso, as respostas continuam saindo como extractos brutos (frente de metadados) porque os próprios chunks top ainda são front matter. Portanto o efeito da camada foi prevenir regressões e preparar a base para novos filtros.
