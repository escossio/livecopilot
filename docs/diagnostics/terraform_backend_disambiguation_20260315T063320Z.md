# Terraform Backend Disambiguation — 20260315T063320Z

## Causa
- `resolve_infra_status_query()` tratava qualquer pergunta com `backend` como consulta operacional de infra.
- A heuristica ignorava o contexto adicional `Terraform` e roubava a pergunta antes da busca semantica.

## Correcao
- `_looks_like_infra_query()` passou a ignorar o gatilho operacional quando a frase contem `terraform` e `backend` juntos.
- A sintese semantica ganhou caso explicito para `backend no Terraform`.

## Before/after
- Antes: backend=`infra_status_connector` | result_count=2 | answer=O backend principal do Livecopilot esta saudavel e respondendo com runtime coerente.
- Depois: backend=`semantic_local` | result_count=3 | answer=No Terraform, backend é o componente que define onde o state fica armazenado e como ele é acessado, podendo ser local ou remoto.