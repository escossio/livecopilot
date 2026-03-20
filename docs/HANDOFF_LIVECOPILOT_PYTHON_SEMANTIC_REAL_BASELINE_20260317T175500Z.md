# Handoff — baseline semântica real do subset Python (2026-03-17T17:55:00Z)

## Objetivo desta rodada
- gerar embeddings contextuais reais para o subset Python validado, manter tudo em `data/semantic_index_experiments/python_pilot/` e comparar lexical vs semântico usando a bateria oficial de oito perguntas sem tocar no índice global.

## Artefatos entregues
- `data/semantic_index_experiments/python_pilot/embeddings.jsonl` (113 chunks com embeddings calculados via `text-embedding-3-large` e segmentação de 1.200 palavras)
- `data/semantic_index_experiments/python_pilot/metadata.json` (modelo, dimensão 3.072, média de ~978 palavras/chunk, timestamp 2026-03-17T17:53:37Z)
- `docs/PYTHON_SEMANTIC_REAL_BASELINE_RESULTS_20260317T175500Z.json` (comparação detalhada para cada pergunta, incluindo ranking lexical e semântico, similaridades e classificações)
- `docs/PYTHON_SEMANTIC_REAL_BASELINE_REPORT_20260317T175500Z.md` (relatório completo desta rodada)
- `docs/HANDOFF_LIVECOPILOT_PYTHON_SEMANTIC_REAL_BASELINE_20260317T175500Z.md` (este arquivo)
- Checkpoint registrado em `STATUS.md` descrevendo a rodada e os testes executados.

## Comparação lexical vs semântica (resumo)
- sete das oito perguntas mantêm o mesmo chunk top em ambos os rankings, com similaridade entre 0.30 e 0.60, ou seja, o embedding real replicou o comportamento lexical validado.
- apenas `pathlib` mudou: o semântico prefere `pathlib-20` (comparações com `os/os.path`) em vez do chunk `pathlib-1`; essa saída ainda traz contexto técnico, mas não responde diretamente “para que serve pathlib?”, resultando na classificação PARCIALMENTE COERENTE.

## Próximo passo sugerido
1. revisar/zoom no chunk `pathlib-20` (e em qualquer outro chunk de módulos longos) para garantir que a versão final do subset oferece um chunk mais direto ao ponto, e rerodar o pipeline de embeddings se necessário.
2. preparar o subset Python para promoção controlada reforçando as perguntas remanescentes (ex.: language_reference) e garantindo que o sandbox será reusado em condições similares antes de integrar ao índice global.
