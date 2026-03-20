# Handoff — Manifesto operacional das fontes Python (2026-03-17T04:20:00Z)

## Situação atual
- A política official-first documentada em `docs/PYTHON_OFFICIAL_SOURCE_POLICY.md` foi convertida em um manifesto executável com URLs, prioridades, lotes e estratégias (`docs/PYTHON_SOURCE_MANIFEST.md`).
- A nova camada JSON (`docs/PYTHON_SOURCE_MANIFEST.json`) serve como entrada para scripts que vão orquestrar os lotes na próxima rodada.

## Artefatos gerados
- `docs/PYTHON_SOURCE_MANIFEST.md`: cada fonte (tutorial, language reference, built-ins/exceptions, módulos críticos, pip, Packaging UG e PEPs) tem nome, categoria, tipo, URLs, disponibilidade, licença, estratégia e prioridade explicitada.
- `docs/PYTHON_SOURCE_MANIFEST.json`: estrutura de dados consistente para pipelines automatizados.

## Lotes de ingestão sugeridos
1. **Lote 1** – documentação oficial de linguagem e módulos essenciais (linguagem, tutorial, built-ins/exceptions, pathlib, subprocess, json, argparse, venv, typing).
2. **Lote 2** – ferramentas de instalação/ambiente (pip e Packaging User Guide).
3. **Lote 3** – PEPs de typing (PEP 484 e PEP 585).

## Próximos passos
1. Validar acessibilidade das URLs e registrar timestamps antes de baixar (próxima etapa documentada neste handoff).
2. Planejar o lote 1 como o próximo freeze parcial, mantendo o domínio Python isolado e sem tocar no índice global.
3. Confirmar a política official-first com o time antes de autorizar o download e o parsing.
