# Semantic intent ranking subset report (20260315T075823Z)

- **Objetivo da rodada:** validar as 10 perguntas parciais alvo após o ajuste de ranking por intenção.
- **Postura:** o backend `semantic_local` foi chamado via `/api/chat` com as perguntas listadas; todas as respostas retornaram `HTTP 200` e usaram o contexto buscado no índice local.
- **Resultado principal:** apesar do boost semântico por intenção, cada resposta ainda sai como `PARCIALMENTE COERENTE`: o texto final permanece ancorado em trechos de documentação ou metadados (front matters) e não entrega uma síntese didática limpa.
- **Próximo passo:** estudar se é possível filtrar diretamente esses front matters antes de ranking ou reforçar o contexto alternativo para as perguntas `what is`/`purpose`/`when to use`.
