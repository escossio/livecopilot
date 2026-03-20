# Semantic regression expanded post intentional ranking (20260315T075856Z)

- **Escopo:** rerun completo das 20 perguntas da baseline expandida após inserir o bônus semântico orientado por intenção.
- **Resumo por domínio:**
  - Terraform: 3 coerentes, 2 parciais.
  - Kubernetes: 3 coerentes, 2 parciais.
  - Docker: 1 coerente, 4 parciais.
  - Observabilidade: 2 coerentes, 2 parciais, 1 falha.
- **Comparação com o baseline anterior (`semantic_regression_expanded_post_synthesis_20260315T072557Z.json`):** os totais permanecem idênticos; não houve regressão, porém também não houve avanço imediato no placar, pois os novos scores ainda privilegiam snippets front matter para as perguntas parciais.
- **Próximo passo recomendado:** aplicar filtros adicionais para remover front matters/metadata dos candidatos ou priorizar chunks alternativos para `o que é`/`para que serve`/`quando usar`, aproveitando o novo esquema de `chunk_type`.
