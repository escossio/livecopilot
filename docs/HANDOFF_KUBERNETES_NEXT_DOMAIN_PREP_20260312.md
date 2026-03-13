# Handoff 2026-03-12 - preparacao do proximo dominio (Kubernetes)

## Objetivo da rodada
Confirmar com evidencia o proximo dominio e deixar pronto o plano controlado de aquisicao/recorte Kubernetes, sem iniciar ingestao.

## Resultado de priorizacao
- `knowledge_gap_engine` atualizado com Kubernetes:
  - `docs/coverage/knowledge_gap_engine_validation_k8s_prep_20260312.json`
- extrato resumido:
  - `docs/coverage/kubernetes_round_prioritization_20260312.json`

Leitura objetiva:
- Por `priority_score` puro, Kubernetes nao e o primeiro.
- Mesmo assim, Kubernetes foi confirmado como proximo dominio por governanca de fonte:
  - top-1 atual em `tmp/*` e `data/raw_review/*`, sem recorte oficial dedicado.

## Fontes oficiais escolhidas
- `kubernetes/website` (docs puro) - fonte primaria para clone.
- `kubernetes.io/docs` (HTML oficial) - referencia complementar.
- `kubernetes/kubernetes` - apenas complemento pontual, fora deste ciclo inicial.

Artefato:
- `docs/coverage/kubernetes_official_sources_mapping_20260312.json`

## Recorte seletivo proposto
- Artefatos:
  - `docs/coverage/kubernetes_docs_selected_proposed_20260312.json`
  - `docs/coverage/kubernetes_docs_selected_proposed_20260312.txt`
- Tamanho: `12` arquivos `.md`.
- Foco: pods, deployments, services, ingress, configmaps, probes, RBAC/service accounts, storage, troubleshooting.
- Diretorio canonico alvo (proxima rodada):
  - `data/knowledge_raw/kubernetes_docs_selected`

## O que nao foi feito nesta rodada
- Nenhuma ingestao canônica foi executada.
- Nenhuma persistencia semantica foi executada.
- Nenhuma alteracao de pipeline.

## Closeout checklist (UTF-8)
- Comando:
```bash
scripts/utf8_hygiene_scan.sh --output docs/coverage/utf8_hygiene_scan_validation_20260312_kubernetes_prep_closeout.json --pretty
```
- Resultado:
  - `total_chunks_scanned=845`
  - `bad_chunks_count=0`
  - `affected_source_files_count=0`
- Status do fechamento: **aprovado**.

## Proximo passo recomendado
1. Clonar `kubernetes/website` em `data/knowledge_raw/_official_repo_clones/kubernetes-website`.
2. Materializar o recorte `kubernetes_docs_selected` com os 12 paths propostos.
3. Executar ingestao canonica controlada e validar parsed/chunks/manifest antes de persistencia semantica.
