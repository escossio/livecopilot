# Handoff: selecao de repositorios oficiais para aquisicao por clone (Kubernetes, Prometheus, Docker, Grafana)

Data: 2026-03-11
Escopo: auditoria e preparacao de fontes oficiais (sem clone massivo, sem ingestao)

## Resultado objetivo por dominio

1) Kubernetes
- Repositorio recomendado: `https://github.com/kubernetes/website`
- Tipo de fonte: docs/site oficial (docs puro)
- Adequacao: o proprio `kubernetes.io/docs` referencia edicao em `kubernetes/website`.
- Recomendacao de aquisicao: **ambos** (HTML espelhado + clone do repo de docs).

2) Prometheus
- Repositorio recomendado: `https://github.com/prometheus/docs`
- Tipo de fonte: docs oficial (docs puro)
- Adequacao: `prometheus.io/docs` referencia pagina fonte em `prometheus/docs`.
- Recomendacao de aquisicao: **ambos** (HTML espelhado + clone do repo de docs).

3) Docker
- Repositorio recomendado: `https://github.com/docker/docs`
- Tipo de fonte: docs oficial (docs puro)
- Adequacao: `docs.docker.com` referencia edicao e issues em `docker/docs`.
- Recomendacao de aquisicao: **ambos** (HTML espelhado + clone do repo de docs).

4) Grafana
- Repositorio recomendado: `https://github.com/grafana/grafana`
- Tipo de fonte: repo principal com documentacao embutida (`docs/sources`) + uso hibrido com HTML
- Adequacao: `grafana.com/docs` referencia edicao em `grafana/grafana`.
- Recomendacao de aquisicao: **hibrido priorizado** (HTML espelhado para cobertura navegacional + clone seletivo do repo principal para conteudo fonte estruturado).

## Validacao minima executada (sem clone)
- Confirmacao de links oficiais em paginas publicas de docs:
  - `kubernetes.io/docs` -> `kubernetes/website`
  - `prometheus.io/docs` -> `prometheus/docs`
  - `docs.docker.com` -> `docker/docs`
  - `grafana.com/docs` -> `grafana/grafana`
- Teste tecnico controlado de acessibilidade remota (sem clone local):
  - `git ls-remote --symref <repo> HEAD` em todos os 4 repositorios
  - todos com `HEAD -> refs/heads/main`.

## Classificacao final de fonte
- Kubernetes: docs puro
- Prometheus: docs puro
- Docker: docs puro
- Grafana: repo principal + hibrido com HTML

## Recomendacao objetiva de proximo dominio para aquisicao
- Proximo dominio recomendado: **Docker**
- Motivo: repo de docs puro, mapeamento oficial direto no site, boa relacao simplicidade/retorno para um primeiro ciclo controlado de clone.

## O que nao mudou
- Nenhuma alteracao de pipeline funcional.
- Nenhuma ingestao iniciada nesta rodada.
- Estrategia hibrida mantida: mesclar, nao substituir.
