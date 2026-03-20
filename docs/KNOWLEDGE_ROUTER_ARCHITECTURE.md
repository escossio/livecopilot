# Knowledge Router Architecture (v1)

Este documento descreve a primeira versão mínima do knowledge router que permite executar a validação manual do roteamento.

## Componentes

1. **Registry** (`app/knowledge/knowledge_front_registry.json`): contém as frentes fechadas, seus índices semânticos, palavras-chave e o flag `enabled_for_routing` que controla quais domínios podem responder consultas.
2. **DomainClassifier** (`app/knowledge/domain_classifier.py`): carrega o registry, filtra apenas frentes habilitadas e pontua cada uma com base em coincidências simples de keywords dentro da query.
3. **KnowledgeRouter** (`app/knowledge/knowledge_router.py`): encapsula o classifier, decide o modo de roteamento (`single_front` quando há score claro; `fallback` caso contrário) e retorna o envelope completo com confiança e candidatos.
4. **Router CLI** (`app/knowledge/router_cli.py`): expõe o roteador via `python -m app.knowledge.router_cli "minha query"`, imprimindo query, frente selecionada, confiança, motivos e candidatos ordenados.

## Fluxo de validação

1. O CLI captura a query do usuário (ex.: "java thread lifecycle").
2. O `KnowledgeRouter` passa o texto para o `DomainClassifier`.
3. O classifier percorre cada frente habilitada, conta quantos keywords casam com a query e monta os candidatos.
4. O router decide o `routing_mode` (single_front quando há score, fallback caso contrário) e devolve um envelope com status e candidatos.
5. O operador compara a frente selecionada com a frente esperada, utilizando o plano de testes atual (`docs/KNOWLEDGE_ROUTER_TEST_PLAN.md`).

## Limitações

- Esta versão ainda não consulta nenhum índice semanticamente; leva em conta apenas keywords para chegar na frente correta.
- O score é linear (1 ponto por keyword) e pode cair em empates quando várias frentes compartilham termos muito genéricos.
- O router não aplica thresholds dinâmicos nem orquestra embeddings.

## Próximos passos futuros

- Substituir o classifier por um modelo semântico que avalia similaridade entre query e chunks.
- Integrar com o pipeline de embeddings para validar automaticamente as queries do plano.
- Registrar métricas de rota (latência, frequência de fallback e mismatches) para guiar refinamentos.
