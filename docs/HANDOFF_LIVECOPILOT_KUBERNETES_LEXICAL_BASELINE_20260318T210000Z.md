# Handoff: Kubernetes Core Lexical Baseline

## Perguntas testadas
- cluster
- node
- pod
- deployment
- service
- namespace
- configmap
- secret
- volumes
- liveness/readiness probes
- kubectl CLI
- manifest YAML

## Cobertura obtida
- `RESPONDIVEL`: 8
- `PARCIALMENTE_RESPONDIVEL`: 3
- `NAO_RESPONDIVEL`: 1

## Lacunas encontradas
- `namespace` não tem chunk suficiente.
- `secret` não tem chunk específico.
- `node` e `service` estão cobertos, mas ainda de forma compacta.

## Pronto para embeddings?
- Parcialmente.
- O domínio já tem base suficiente para continuar, mas vale um refinement mínimo antes de embeddings se a meta for reduzir ruído em `namespace` e `secret`.

## Estado da frente
- `lexical_baseline` concluída.
- corpus não foi expandido nesta rodada.
