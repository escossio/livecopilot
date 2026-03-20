# FRONT OPENAI_PRODUCTS

## Objetivo
- Estruturar e governar a frente de conhecimento sobre produtos e APIs da OpenAI, incluindo CODEX, com foco em documentação técnica oficial.

## Escopo
- Inclui: OpenAI API docs, modelos, embeddings, realtime API, áudio, imagem, limites/quotas, pricing, guias técnicos oficiais e posts técnicos oficiais relevantes.
- Inclui explicitamente CODEX (app, CLI, IDE extension, cloud/delegated tasks, security, prompting guide, changelog, modelos como gpt-5.3-codex).
- Exclui: tutoriais externos, cursos, vídeos, blogs/opinião, qualquer conteúdo não oficial ou promocional.

## source_policy
- Fontes permitidas: apenas domínios oficiais da OpenAI (docs.openai.com, platform.openai.com, openai.com/blog, developers.openai.com, help.openai.com) e páginas oficiais de CODEX listadas.
- Conteúdo deve ser técnico, rastreável, com versão/data quando disponível.
- Evitar conteúdo promocional/marketing; priorizar páginas de referência, guias técnicos e notas de uso/limites.
- CODEX está incluído desde que a fonte seja oficial OpenAI.

## source_manifest (candidatos iniciais)
- API Reference (REST) – endpoints, autenticação, rate limits.
- Models – especificações e uso dos modelos atuais.
- Embeddings – guia e referência de embeddings.
- Realtime API – documentação oficial de streaming.
- Audio & Speech – transcrição, TTS, audio generation.
- Images – geração e parâmetros de safety.
- Rate limits & usage policies – seções oficiais de limites, políticas e preços.
- Oficial tech blog posts relevantes (ex.: anúncios técnicos de API/modelos) quando necessários para contexto.
- CODEX fontes oficiais:
  - https://openai.com/codex/
  - https://openai.com/index/introducing-codex/
  - https://openai.com/index/introducing-the-codex-app/
  - https://developers.openai.com/codex/ide/
  - https://developers.openai.com/codex/changelog/
  - https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide/
  - https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
  - https://help.openai.com/en/collections/14937394-codex
  - https://openai.com/index/introducing-gpt-5-3-codex/

## corpus_lock (inicial)
- Aprovadas para materialização: docs.openai.com (referência, guias), platform.openai.com (API, modelos, embeddings, realtime, audio, images, limits/pricing), developers.openai.com (CODEX IDE/CLI/changelog/prompting), help.openai.com (artigos oficiais sobre CODEX), openai.com/blog e openai.com/index para posts técnicos oficiais, incluindo CODEX.
- Fora do lock: qualquer fonte não oficial, tutoriais de terceiros, vídeos, cursos, fóruns, conteúdos promocionais não técnicos.

## Status atual
- `closed`

## Lifecycle oficial
1. source_policy
2. source_manifest
3. corpus_lock
4. parsing
5. chunking
6. lexical_baseline
7. semantic_embeddings
8. semantic_baseline
9. closure_decision

- ## semantic_embeddings
- ### Situação da etapa
- Embeddings gerados sobre os 122 chunks validados da frente OPENAI_PRODUCTS.
- ### Artefatos
- - `data/semantic_index_experiments/openai_products/embeddings.jsonl`
- - `data/semantic_index_experiments/openai_products/metadata.json`
- - Relatório: `docs/OPENAI_PRODUCTS_EMBEDDINGS_REPORT.md`
- ### Observações
- - Modelo `text-embedding-3-large`, dimensão 3072.
- - Todas as unidades do chunking foram tratadas; não houve falhas.
- ### Próximos passos
- - `semantic_baseline`

-## semantic_baseline
-### Situação da etapa
-Executada sobre `data/semantic_index_experiments/openai_products/` (122 embeddings).
-### Relatórios
- - `docs/OPENAI_PRODUCTS_SEMANTIC_BASELINE_REPORT.md`
- - `docs/OPENAI_PRODUCTS_SEMANTIC_BASELINE_RESULTS.json`
-### Achados
- - Todas as 12 consultas ficaram `COERENTE`; top chunks vieram de API docs, policies e Codex.
- - Nenhuma lacuna crítica detectada; cobertura equilibrada entre APIs, modelos, políticas e Codex.
-### Decisão
- - baseline aprovado; próximo passo oficial: `closure_decision`.

- ## closure_decision
- - Status: `closed`
- - Relatório final: [`docs/OPENAI_PRODUCTS_FINAL_REPORT_20260319T050414Z.md`](/lab/projects/livecopilot/docs/OPENAI_PRODUCTS_FINAL_REPORT_20260319T050414Z.md)
- - Handoff: [`docs/HANDOFF_LIVECOPILOT_OPENAI_PRODUCTS_FRONT_CLOSURE_20260319T050414Z.md`](/lab/projects/livecopilot/docs/HANDOFF_LIVECOPILOT_OPENAI_PRODUCTS_FRONT_CLOSURE_20260319T050414Z.md)
- - Decisão: cobertura completa do corpus técnico oficial, baseline semântico aprovado.
