# Semantic regression expanded post bad chunk filter (20260315T081014Z)

- **Escopo:** rerun completo das 20 perguntas da baseline expandida depois de aplicar o filtro/penalidade para chunks estruturalmente ruins.  
- **Resumo por domínio:**
  - Terraform: 3 coerentes, 2 parciais.  
  - Kubernetes: 3 coerentes, 2 parciais.  
  - Docker: 1 coerente, 4 parciais.  
  - Observabilidade: 2 coerentes, 2 parciais, 1 falha.  
- **Comparação com a baseline anterior (`semantic_regression_expanded_post_intent_ranking_20260315T075856Z.json`):** os totais permanecem os mesmos; o filtro não converteu parciais em coerentes, mas garantiu que os snippets front matter recebam penalidade alta (0.28–0.6) enquanto o ranking mantém a ordem dos demais candidatos.  
- **Observação:** os 9 casos que permanecem parciais ainda dependem de chunk cleaner (conteúdo útil ausente), mas o filtro impede regressões futuras ao exigir que qualquer chunk novo seja mais limpo que a metadata penalizada.  
