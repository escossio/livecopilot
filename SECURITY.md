# Security Policy

## Reportar vulnerabilidades

Para reportar vulnerabilidades, abra um canal privado com os mantenedores e descreva:

- impacto observado
- superficie afetada
- passos para reproduzir
- mitigacao sugerida (se houver)

Evite publicar detalhes exploraveis em issue publica antes da triagem.

## Escopo

Esta politica cobre:

- codigo em `app/`, `scripts/`, `config/`
- workflow CI em `.github/workflows/`
- superficies HTTP e WebSocket da aplicacao

Fora de escopo inicial:

- hardening de infraestrutura externa nao versionada neste repositorio
- segredos locais acidentalmente configurados fora do repo
