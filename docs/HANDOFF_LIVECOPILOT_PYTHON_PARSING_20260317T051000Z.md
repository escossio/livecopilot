# Handoff — Parsing do corpus Python Lote 1 (2026-03-17T05:10:00Z)

## Situação atual
- A Etapa 4 aplicou a política de parsing estabelecida em `docs/PYTHON_PARSING_POLICY.md` ao corpus bruto congelado em `data/knowledge_raw/python/`.
- O resultado está em `data/knowledge_parsed/python/`, mantendo a mesma hierarquia (`tutorial/`, `language_reference/`, `builtins_exceptions/`, `modules/{pathlib,subprocess,json,argparse,venv,typing}`) e liberando conteúdo limpo para o próximo chunking.

## Política e amostras
- `docs/PYTHON_PARSING_POLICY.md` descreve a remoção de navegação, breadcrumbs, scripts e sidebars, preservando headings, assinaturas e blocos explicativos.
- `docs/PYTHON_PARSING_SAMPLE_REPORT_20260317T050500Z.md` compara antes/depois nas páginas do tutorial, language reference, built-ins/exceptions e pathlib, mostrando que o parseado está mais chunkável e responde mais diretamente.

## Próximos passos sugeridos
1. Planejar o chunking controlado do Lote 1 usando `data/knowledge_parsed/python/` como fonte limpa e `docs/PYTHON_CORPUS_LOCK.md` como referência de integridade.
2. Garantir que qualquer re-parsing ou recaptura siga a mesma política antes de atualizar os artefatos derivados.
3. Rever e aprovar o pipeline de chunking antes de gerar embeddings ou tocar o índice global.
