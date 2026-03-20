# Handoff — Chunking piloto do corpus Python Lote 1 (2026-03-17T05:35:00Z)

## Situação atual
- A Etapa 5 gerou a primeira camada de chunks a partir do corpus parseado em `data/knowledge_parsed/python/`, limitando-se ao subset oficial do Lote 1 (tutorial, language reference, built-ins/exceptions e quatro módulos: pathlib, subprocess, json, argparse).
- Cada chunk segue a política descrita em `docs/PYTHON_CHUNKING_POLICY.md` e está listado em `docs/PYTHON_CHUNKING_METADATA.json` com metadados auditáveis.

## Subset piloto
- `data/knowledge_chunks/python/` contém diretórios para cada família; dentro deles, JSONs com texto e metadados (`source_family`, `source_file`, `chunk_id`, `title`, `section`, `length`).
- O subset inclui: 1 chunk per heading em `tutorial/index.html`, `language_reference/index.html`, `builtins_exceptions/functions.html`, e nos módulos pathlib/subprocess/json/argparse.
- O relatório `docs/PYTHON_CHUNKING_SAMPLE_REPORT_20260317T053000Z.md` documenta amostras comparativas antes/depois e mostra que os chunks mantêm contexto útil.

## Próximos passos sugeridos
1. Validar lexicalmente o subset chunked (perguntas-chave com `scripts/c_domain_query.py` adaptado a Python) antes de expandir o scope.
2. Confirmar se novos chunkings devem seguir a mesma granularidade ou se cabe ajustar o tamanho máximo dos chunks.
3. Assim que o subset for aprovado, gerar embeddings/local persistence sem tocar no índice global.
