# Semantic intent ranking diagnostic (2026-03-15T07:56Z)

- **Objetivo:** confirmar se os chunks top-of-mind atendem à intenção da pergunta e, quando não atendem, mostrar o tipo ideal esperado.
- **Contexto técnico:** as respostas do subset continuam parciais mesmo com limpeza, síntese por intenção e LLM; os snippets são predominante front matters ou definições desalinhadas.

| Domínio | Pergunta | Intenção detectada | Tipo do chunk atual | Tipo ideal | Mismatch | Direção observada |
| --- | --- | --- | --- | --- | --- | --- |
| Terraform | Quando usar modulos no Terraform? | when_to_use | use | use | não | aligned |
| Terraform | O que e um workspace no Terraform? | what_is | noise (front matter) | definition | sim | noise → definition |
| Kubernetes | Para que serve um Deployment no Kubernetes? | purpose | definition | purpose | sim | definition → purpose |
| Kubernetes | Quando usar um Ingress no Kubernetes? | when_to_use | definition | use | sim | definition → use |
| Docker | O que e port publishing no Docker? | what_is | noise (front matter) | definition | sim | noise → definition |
| Docker | O que e o host network driver no Docker? | what_is | noise (front matter) | definition | sim | noise → definition |
| Docker | Para que serve o modo rootless no Docker? | purpose | noise (front matter) | purpose | sim | noise → purpose |
| Docker | O que e content trust no Docker? | what_is | noise (front matter) | definition | sim | noise → definition |
| Observabilidade | O que e uma alerting rule no Prometheus? | what_is | noise (front matter) | definition | sim | noise → definition |
| Observabilidade | O que e uma notification policy no Grafana Alerting? | what_is | noise (front matter) | definition | sim | noise → definition |

- **Leitura:** exceto pelo primeiro item, a intenção percebida não casa com o tipo de chunk escolhido: ou o chunk é apenas metadata/front matter ou entrega definição quando a pergunta pedía finalidade/uso. O ajuste proposto irá inclinar o ranking para chunks que realmente respondem à intenção detectada.
