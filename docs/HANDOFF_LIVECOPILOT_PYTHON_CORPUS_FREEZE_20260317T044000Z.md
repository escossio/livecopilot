# Handoff — Congelamento do corpus Python (Lote 1, 2026-03-17T04:40:00Z)

## Situação atual
- A Etapa 3 do domínio Python congelou o Lote 1 oficial (tutorial, language reference, built-ins/exceptions e os módulos pathlib, subprocess, json, argparse, venv, typing) em `data/knowledge_raw/python/`.
- Cada artefato foi salvo em diretórios separados, com metadata (`data/knowledge_raw/python/metadata/*.json`), hashes SHA256 e registro no lockfile (`docs/PYTHON_CORPUS_LOCK.md`/`.json`).

## Corpus congelado
- Diretórios criados: `tutorial/`, `language_reference/`, `builtins_exceptions/`, `modules/{pathlib,subprocess,json,argparse,venv,typing}`.
- Lockfile e JSON (`docs/PYTHON_CORPUS_LOCK.*`) documentam as fontes congeladas, seus hashes, tamanhos e URLs. Todos os arquivos do lote 1 foram capturados sem erros.
- Os metadados (`data/knowledge_raw/python/metadata/`) podem alimentar scripts posteriores e garantem rastreabilidade de versão.

## Fontes pendentes
- Lotes 2 e 3 (pip, Packaging User Guide, PEP 484 e PEP 585) ficaram aguardando a próxima autorização antes do download.

## Próximo passo sugerido
1. Planejar o parsing/limpeza do Lote 1 usando o lockfile como referência e manter backup do corpus bruto.
2. Validar a integridade do lote 1 (hashes em `docs/PYTHON_CORPUS_LOCK.md`) antes de iniciar chunking ou embeddings.
3. Reavaliar o manifesto em caso de novas versões do Python ou alterações relevantes nos módulos listados.
