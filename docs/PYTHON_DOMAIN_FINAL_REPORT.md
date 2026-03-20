# Python domain final report — 2026-03-17T18:00:00Z

## Contexto
- o piloto Python seguiu a sequência oficial-first → freeze de corpus → parsing → chunking → validação lexical → refinamento → baseline semântica real, tudo isolado do índice global.
- os artefatos oficiais (corpus lock, manifesto de fontes, chunking policies) já estavam disponíveis e foram referenciados ao longo do ciclo para garantir rastreio completo.

## Pipeline executado
1. **Fontes oficiais** – conforme `docs/PYTHON_SOURCE_MANIFEST.md` e `docs/PYTHON_OFFICIAL_SOURCE_POLICY.md`, priorizamos apenas fontes autorizadas.
2. **Congelamento do corpus** – o `docs/PYTHON_CORPUS_LOCK.md` registra hashes e Lote 1 inteiro.
3. **Parsing controlado** – versões limpas no pipeline foram documentadas em `docs/PYTHON_PARSING_POLICY.md`.
4. **Chunking piloto** – `docs/PYTHON_CHUNKING_POLICY.md` e `docs/PYTHON_CHUNKING_METADATA.json` reúnem as 113 entradas do subset.
5. **Validação lexical** – `docs/PYTHON_CHUNK_LOCAL_VALIDATION_REPORT_20260317T130000Z.md` confirma cobertura das 8 perguntas.
6. **Refinamento** – os conceitos chave ampliados constam em `docs/PYTHON_CHUNK_REFINEMENT_REPORT_20260317T190000Z.md` e nos resultados JSON.
7. **Baseline semântica real** – ver `docs/PYTHON_SEMANTIC_REAL_BASELINE_REPORT_20260317T175500Z.md` e o sandbox `data/semantic_index_experiments/python_pilot/` com embeddings `text-embedding-3-large` e dimensão 3.072.

## Resultados da baseline semântica
- perguntas avaliadas: módulo, exceção, pathlib, subprocess.run, json.dumps, argparse, venv, typing.
- 7/8 com alinhamento lexical vs semântico (mesmo chunk top, similaridade 0.30–0.60).
- `pathlib` ficou `pathlib-20` (comparativo com os/os.path) e foi classificado como PARCIALMENTE COERENTE.
- Detalhes completos em `docs/PYTHON_SEMANTIC_REAL_BASELINE_RESULTS_20260317T175500Z.json`.

## Pendências conhecidas
- criar ou ajustar o chunk conceitual de `pathlib` para responder diretamente “para que serve pathlib?” e rerodar o ranking se necessário.
- revisar a segmentação de chunks longos (builtins/functions, módulos extensos) para garantir amplitudes coerentes com o embedding real.
- planejar futura ampliação do corpus Python quando novas fontes oficiais estiverem validadas.
- monitorar o comportamento semântico em perguntas fora da bateria atual (language_reference, builtins ampliados, etc.).

## Conclusão
- o domínio Python está documentado como concluído: a baseline semântica real foi gerada em sandbox isolado, o subset lexical foi validado e as etapas estão rastreadas.
- as pendências são pontuais (principalmente `pathlib`) e podem ser tratadas sem reabrir o pipeline inteiro; o domínio pode ser promovido quando esses ajustes forem feitos.
