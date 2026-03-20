# Handoff Pipeline Lab — UI mínima

## O que a UI mostra
- lista de runs disponíveis, sua cor de status e stage atual (painel lateral).
- detalhes da run selecionada: ID, domínio, stage, status e timestamp inicial.
- histórico (`executed_stages`) e resumo (último resultado) no painel central.
- log textual com cada stage executado, permitindo acompanhar a sequência de eventos.

## Dados consumidos
- `GET /api/runs` lista as runs e permite montar os botões laterais.
- `GET /api/runs/:id` traz stage/status atuais e metadata (`executed_stages`) para povoar histórico, log e summary.
- um fallback embutido replica a run `fd999231-...` caso o servidor HTTP ainda não esteja exposto.

## Limitações atuais
- o backend HTTP ainda não existe, então a UI depende de fetchs que podem falhar e voltar ao fallback.
- não há pagination, filtros ou autenticação nesta tela.
- o log é construído apenas a partir do metadata salvo na run; não há chamada adicional ao filesystem.

## Próximos passos sugeridos
- publicar um servidor simples (`FastAPI`/`Flask`) que sirva `/api/runs` e `/api/runs/{id}` e permita carregar a UI real.
- incluir um botão para avançar o stage atual via API e atualizar a interface em seguida.
- adicionar indicador visual de divergências ou bloqueios.
