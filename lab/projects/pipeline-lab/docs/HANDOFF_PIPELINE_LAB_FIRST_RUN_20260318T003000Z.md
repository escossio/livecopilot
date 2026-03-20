# Handoff Pipeline Lab — primeira run operacional

## Objetivo da rodada
Provar o fluxo mínimo: carregar o domínio Terraform, criar a run via API, registrar stage/status e persistir summary/artifacts/logs no diretório `runs/`.

## Domínio usado
`terraform` (current_stage: providers_pending)

## Run criada
- ID: fd999231-3b52-42a8-96f6-2dc761cc9a71
- Stage/status gravados em `app/storage/runs.json`
- Sumário salvo em `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/summary.json`
- Artefatos mínimos (`artifacts.json`, `log.txt`) criados no mesmo diretório

## O que funciona hoje
- Carregamos o domínio via `domain_loader.load_domain`
- A API `routes.create_run` inicia o Runner e o `routes.get_runs` retorna o histórico
- Run armazenada em JSON e replicada em pasta `runs/<id>` com summary/log/artifacts

## Próximos passos para evoluir
- Registrar status avançados (divergências, completed, etc.) no metadata
- Criar serviços para avançar etapas e gerar artefatos reais
- Construir UI/runner mínimos e conectar a `runs/` para supervisão visual
