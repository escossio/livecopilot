# Handoff Pipeline Lab — esqueleto operacional

## Objetivo da rodada
Entregar a estrutura inicial do projeto Pipeline Lab como base para registrar domínios, runs e artefatos antes que a frente evolua para runner/API/UI.

## Artefatos gerados
- `lab/projects/pipeline-lab/README.md`
- `lab/projects/pipeline-lab/STATUS.md`
- `lab/projects/pipeline-lab/pyproject.toml`
- `lab/projects/pipeline-lab/docs/*` (projetos de escopo, protocolo, gates, schema e daily usage)
- `lab/projects/pipeline-lab/domains/*.yaml`
- `lab/projects/pipeline-lab/app/` (core, services, storage, api, web)
- `lab/projects/pipeline-lab/runs/.gitkeep`
- `lab/projects/pipeline-lab/tests/*.py`

## Papel do esqueleto
Estrutura modular para definir domínios, iniciar runs, verificar gates e registrar artefatos, mantendo logs e testes básicos para garantir que a frente Pipeline Lab esteja pronta para evoluir em rodadas futuras.

## Próximos passos sugeridos
- definir protocolos de execução em mais detalhes e preencher os docs de `PROJECT_SCOPE`/`EXECUTION_PROTOCOL`
- implementar runner mínimo com conexão à API e UI
- registrar domínios reais em `domains/`
- criar pipelines de testes e validações adicionais
