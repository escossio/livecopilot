# Python semantic baseline — 2026-03-17T19:00:00Z

## Contexto
- o subset Python já estava aferido lexicalmente (relatórios das 13h00 e 19h00) e agora iremos montar um sandbox semântico local para comparar o comportamento das buscas com a mesma bateria oficial de oito perguntas.
- o objetivo é manter o índice global intacto, criar embeddings apenas sobre o subset pilotado e determinar em que situações (se houver) o retrieval semântico supera o lexical.

## Embeddings e índice isolado
- diretório: `data/semantic_index_experiments/python_pilot/`; arquivos gerados: `embeddings.jsonl` (113 chunks com {chunk_id, família, título, trecho, embedding}) e `metadata.json` (modelo `tfidf-v1`, dimensão 2048, média de ~869 tokens por chunk, vocabulário top 2048). 
- o embedding é uma vetorização TF-IDF construída a partir dos tokens dos chunks, normalizada e mantida local para evitar qualquer interferência no banco principal.

## Comparação lexical vs semântica
1. **O que é um módulo em Python?** – lexical: `tutorial_module_concept_chunk_1.json`; semântico: `argparse-3` (similaridade 0.097, `FALHA`).
2. **O que é uma exceção em Python?** – lexical: `builtins_exceptions_concept_chunk_1.json`; semântico: `argparse-3` (similaridade 0.045, `FALHA`).
3. **Para que serve pathlib?** – lexical: `pathlib-1`; semântico: `argparse-29` (0.145, `FALHA`).
4. **O que `subprocess.run()` faz?** – lexical: `subprocess-1`; semântico: `subprocess-9` (0.245, `FALHA`).
5. **Para que serve `json.dumps()`?** – lexical: `json-1`; semântico: `argparse-14` (0.070, `FALHA`).
6. **O que `argparse` faz?** – lexical: `argparse-1`; semântico: `argparse-51` (0.165, `FALHA`).
7. **Para que serve venv?** – lexical: `venv-1`; semântico: `builtins_functions-1` (0.000, `FALHA`).
8. **O que typing faz?** – lexical: `typing-1`; semântico: `argparse-9` (0.073, `FALHA`).

As respostas semânticas ficaram irrelevantes porque o modelo TF-IDF favoreceu seções curtas de `argparse` que compartilham poucos tokens com as perguntas; o ranking lexical segue sendo o único que devolve chunks focados no conceito solicitado.

## Resumo por família
- **tutorial**: a pergunta sobre módulo está bem coberta lexicalmente; o semântico se confunde com `argparse`, o que evidencia que o vetor precisa de melhor sinal semântico (TF-IDF está cedo demais).
- **language_reference**: nenhuma pergunta desta rodada depende diretamente da language reference, portanto o comportamento permanece inalterado.
- **builtins_exceptions**: o chunk `exceptions-concept-1` continua o topo lexical; semântico, por falta de contexto, recai em entradas de `argparse` com baixa similaridade.
- **modules**: as quatro perguntas restantes (pathlib, subprocess, json, argparse, venv, typing) têm o mesmo top lexical e o semântico colhe outros tópicos do módulo `argparse` com similaridade <0.25, mostrando que o embedding precisa de mais informação contextual ou modelo distinto.

## Conclusão
- A baseline semântica local foi montada (TF-IDF + índice isolado) e executada na bateria. O ranking lexical ainda domina todas as perguntas porque o TF-IDF não captura as relações conceituais necessárias; o semântico falha de forma consistente (classificações `FALHA`).
- Antes de colar este subset no pipeline global, recomendamos experimentar embeddings mais contextuais (p. ex. modelos pré-treinados) ou reforçar o vocabulário com bigramas/trigramas para que a similaridade semântica deixe de privilegiar o `argparse`.
