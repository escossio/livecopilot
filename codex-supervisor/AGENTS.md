# AGENTS

## Escopo

Este repositório (`codex-supervisor`) é o orquestrador local. Ele não é o projeto-alvo.

## Regras operacionais

- O projeto-alvo é sempre externo e definido por caminho (`TARGET_PROJECT_PATH`).
- Não mover ou copiar arquivos do projeto-alvo para este repositório.
- Estado e checkpoints ficam somente em `state/`.
- Logs ficam somente em `logs/`.
- Não confundir `codex-supervisor` com o workspace do projeto-alvo durante leituras/escritas.
- Nesta fase, qualquer ação no projeto-alvo deve ser deliberada, mínima e conservadora.
