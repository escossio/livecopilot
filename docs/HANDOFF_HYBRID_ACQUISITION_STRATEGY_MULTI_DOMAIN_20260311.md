# Handoff: expansao multi-dominio da estrategia hibrida de aquisicao documental

Data: 2026-03-11
Escopo: formalizacao documental/arquitetural (sem alteracao de pipeline)

## Resumo curto
- O padrao adotado para Terraform foi generalizado para outros dominios tecnicos.
- Regra oficial mantida: **mesclar, nao substituir**.
- HTML oficial espelhado continua caminho valido.
- Repo oficial clonado passa a ser caminho complementar quando a fonte for mais limpa/estruturada.

## Dominios formalmente cobertos
- Kubernetes
- Prometheus
- Grafana
- Docker
- Ansible
- PostgreSQL

## Regras consolidadas por dominio
- HTML espelhado: valido.
- Repo oficial clonado: complementar.
- Escolha da origem: qualidade estrutural + fidelidade do conteudo publicado + deduplicacao por conteudo/origem.
- Coexistencia das duas abordagens: permitida.

## O que nao mudou
- Nenhuma abordagem anterior foi removida.
- Nenhuma logica funcional do pipeline foi alterada.
- Nenhuma aquisicao real de conteudo foi iniciada nesta rodada.
