# Semantic Fallback Analysis — 2026-03-15T05:41:00Z

## Onde o fallback entra
- `generate_suggestions()` tenta primeiro `_search_semantic_local_with_context()`.
- Se isso falhar por excecao, tenta `_search_semantic_api_with_context()`.
- Se ambos falharem por excecao, cai para `search_knowledge_chunks_with_debug()`.

## O que aconteceu nos canarios
- Nao houve fallback lexical por excecao.
- A busca vetorial respondeu com sucesso para Terraform e Kubernetes.
- Mesmo assim, Terraform terminou com `result_count=0` porque os `matches` foram anulados apos `_passes_domain_gating()`.
- Em Kubernetes, houve contexto, mas a resposta final seguiu generica porque `_build_knowledge_enriched_suggestions()` coloca o texto contextualizado no slot 1 e `_build_livecopilot_reply()` consome o slot 0.

## Fallback generico de resposta
- Quando nao ha `topic`, `_build_knowledge_enriched_suggestions()` define o slot curto como:
  - `Pelo contexto técnico, o caminho mais seguro é começar por fundamentos e validar em ambiente controlado.`
- Quando ha `topic`, o slot curto vira a frase generica do topico.
- Em ambos os casos, o slot curto pode mascarar o estado real da busca: ou contexto foi bloqueado, ou contexto existe mas nao foi promovido a resposta principal.

## Efeito operacional
- Terraform: aparencia de resposta vaga causada por `domain_gating` zerando resultados e pela resposta curta de topico.
- Kubernetes: aparencia de resposta vaga causada por selecao do slot errado, nao por ausencia de contexto.
