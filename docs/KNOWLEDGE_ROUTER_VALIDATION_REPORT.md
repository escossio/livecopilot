# Knowledge Router Validation Report v1

## Objetivo
Validar a execução do knowledge router mínima (app/knowledge/router_cli.py) usando as queries representativas documentadas em `docs/KNOWLEDGE_ROUTER_TEST_PLAN.md` e registrar o comportamento observado para cada frente habilitada.

## Resultados
| Query | Frente esperada | Frente selecionada | Status | Observações |
| --- | --- | --- | --- | --- |
| How do I chain Stream.map, filter and collect to accumulate results? | JAVA | JAVA | OK | matched keywords `stream map`, `stream filter`, `collect`; rotas respeitam keywords expandidos. |
| How can I stream ChatCompletions responses on the new OpenAI Realtime API? | OPENAI_PRODUCTS | OPENAI_PRODUCTS | OK | múltiplos keywords de `openai / realtime api / chatcompletions` superam outros; aposta single_front. |
| What is the difference between terraform plan and terraform apply, and when do I use workspaces? | TERRAFORM | TERRAFORM | OK | cada tópico (`plan`, `apply`, `workspaces`) foi pontuado e a confiança alcança 1.0. |
| What does a multi-stage Dockerfile look like for a Go binary? | DOCKER | DOCKER | OK | keywords adicionais `dockerfile`, `multi-stage`, `bind mount` solidificam o ranking. |
| When should I use a StatefulSet instead of a Deployment in Kubernetes? | KUBERNETES | KUBERNETES | OK | alias `kubernetes` + keyword `statefulset` prevalecem. |
| When should I use asyncio.run instead of manually driving the event loop? | PYTHON | PYTHON | OK | `asyncio` keyword e alias confirmam a frente. |
| How should I index a JSONB column for fast querying in PostgreSQL? | POSTGRESQL | POSTGRESQL | OK | keywords `jsonb`, `jsonb indexing`, `postgresql sql` geram score alto. |
| Which systemd unit type handles a oneshot command, and how is it configured? | LINUX | LINUX | OK | keywords `systemd`, `oneshot`, `command line` guiam a escolha. |
| What does the assert macro do when the condition fails in C? | Nenhuma (`C_PILOT` está desabilitado) | fallback | OK | nenhuma frente habilitada pontuou, `C_PILOT` não aparece na lista de candidatos. |

## Observações gerais
- O router só tentou frentes com `enabled_for_routing=true`; a lista de candidatos retornada pelo CLI mostra exatamente os oito domínios habilitados (C_PILOT foi omitido).  
- O modo de roteamento permaneceu `single_front` sempre que houve score e `fallback` apenas para a query de C.  
- Não houve mismatches; portanto, `knowledge_router_v1_validated = true`.  
