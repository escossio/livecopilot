# Handoff — baseline semântica do subset Python (2026-03-17T19:00:00Z)

## Objetivo desta rodada
- montar uma trilha isolada em `data/semantic_index_experiments/python_pilot/` para gerar embeddings e comparar retrieval lexical versus semântico usando os oito questionamentos oficiais do subset Python.

## Artefatos entregues
- `data/semantic_index_experiments/python_pilot/embeddings.jsonl` (113 chunks com vetores TF-IDF, metadados e texto completo)
- `data/semantic_index_experiments/python_pilot/metadata.json` (modelo `tfidf-v1`, dimensão 2048, média de ~869 tokens, timestamp 2026-03-17T17:15:14Z)
- `docs/PYTHON_SEMANTIC_BASELINE_RESULTS_20260317T190000Z.json` (comparação detalhada de cada pergunta, com top chunk lexical e semântico, similaridades e classificações)
- `docs/PYTHON_SEMANTIC_BASELINE_REPORT_20260317T190000Z.md` (relatório que resume o experimento, as similaridades e o resumo por família)
- `docs/HANDOFF_LIVECOPILOT_PYTHON_SEMANTIC_BASELINE_20260317T190000Z.md` (este arquivo)
- Checkpoint registrado em `STATUS.md` explicando a rodada.

## Comparação lexical vs semântica (resumo)
- Apesar de um índice TF-IDF local com vocabulário top 2048, o semantic search favoreceu sub-seções de `argparse` (diferentes chunk_ids) com similaridade abaixo de 0.25 para todas as questões; como os vetores são poucos semânticos, a classificação do semântico foi `FALHA` em todas as perguntas.
- O ranking lexical continua a devolver módulos/tópicos específicos (`tutorial-module-1`, `exceptions-concept-1`, `pathlib-1`, etc.), enquanto o semântico ainda confunde os conceitos, o que significa que o subset não está pronto para mover o domínio ao índice global.

## Próximo passo sugerido
- experimentar embeddings mais contextuais (ex.: modelos Hugging Face, embeddings de frases) ou enriquecer o vocabulário (bigramas/trigramas) para que a similaridade semântica reflita melhor as perguntas.
- manter o sandbox isolado em `data/semantic_index_experiments/python_pilot/` até que o índice semântico esteja consistente; em seguida, avaliar os próximos domínios a serem adicionados.
