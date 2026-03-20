# Python semantic real baseline — 2026-03-17T17:55:00Z

## Contexto
- o subset Python já validado lexicalmente (módulo, exceção, pathlib, subprocess, json, argparse, venv, typing) foi preservado, e agora alimentamos um sandbox semântico real para comparar a mesma bateria oficial de oito perguntas.
- o objetivo é confirmar que embeddings contextuais de verdade (não TF-IDF) mantêm ou superam o ranking lexical, tudo em um índice isolado (`data/semantic_index_experiments/python_pilot/`) que nunca toca no banco legado.

## Embeddings e índice isolado
- diretório: `data/semantic_index_experiments/python_pilot/` com as tabelas `embeddings.jsonl` e `metadata.json` marcando a nova baseline.
- modelo: `text-embedding-3-large`; cada chunk é dividido em segmentos de até 1.200 palavras para respeitar o limite de 8.192 tokens, os embeddings dos segmentos são agregados por média e armazenados em registros com `chunk_id`, família, título, seção e texto.
- metadados: 113 chunks, dimensão 3.072, média de ~978 palavras por chunk; timestamp de geração 2026-03-17T17:53:37Z.

## Comparação lexical vs semântica
1. **O que é um módulo em Python?** – lexical: `tutorial-module-1`; semântico: `tutorial-module-1` (similaridade 0.4342, COERENTE).
2. **O que é uma exceção em Python?** – lexical: `exceptions-concept-1`; semântico: `exceptions-concept-1` (0.5269, COERENTE).
3. **Para que serve pathlib?** – lexical: `pathlib-1`; semântico: `pathlib-20` (0.5304, PARCIALMENTE COERENTE, pois discute comparativos com `os/os.path`).
4. **O que `subprocess.run()` faz?** – lexical: `subprocess-1`; semântico: `subprocess-1` (0.5040, COERENTE).
5. **Para que serve `json.dumps()`?** – lexical: `json-1`; semântico: `json-1` (0.4283, COERENTE).
6. **O que `argparse` faz?** – lexical: `argparse-1`; semântico: `argparse-1` (0.5034, COERENTE).
7. **Para que serve venv?** – lexical: `venv-1`; semântico: `venv-1` (0.6005, COERENTE).
8. **O que typing faz?** – lexical: `typing-1`; semântico: `typing-1` (0.3091, COERENTE).

## Resumo por família
- **tutorial**: a pergunta sobre módulos continua sendo respondida pelo mesmo chunk introdutório; a semântica real confirma que o vetor reconhece o conceito central.
- **language_reference**: nenhuma pergunta da bateria toca diretamente esse corpo, mas o índice permanece disponível para consultas futuras sem regressão.
- **builtins_exceptions**: o chunk `exceptions-concept-1` segue liderando em lexical e semântico, mostrando que a representação contextual internalizou as relações de exceção/base.
- **modules**: cinco dos seis módulos (subprocess, json, argparse, venv, typing) tiveram o mesmo chunk em ambos os rankings, com similaridades entre 0.30 e 0.60; `pathlib` ainda retorna uma seção comparativa (`pathlib-20`), então requer refinamento antes de promover.

## Conclusão
- o baseline semântico real foi montado (texto segmentado + `text-embedding-3-large`) e a bateria foi rerodada. Sete das oito perguntas produzem o mesmo topo lexical, sinalizando que a vetorização contextual já acompanha o conteúdo validado.
- o único alerta é `pathlib`, cujo vetor real privilegia um capítulo de comparação com `os/os.path`; o ranking lexical permanece superior nesse caso, então vale reforçar ou re-chunkar esse material antes de subir o subset para o índice global.
- portanto, o subset Python está pronto para avançar com esse sandbox semântico isolado, mantendo sob observação os casos `pathlib` e qualquer família que ainda não tenha pergunta oficial (language_reference, builtins_exceptions ampliadas, etc.).
