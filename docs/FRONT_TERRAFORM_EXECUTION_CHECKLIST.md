# Checklist da Frente Terraform

## 1) IDENTIFICAÇÃO DA FRENTE
- **nome:** Terraform
- **objetivo:** documentar e concluir a coleta, chunking e validação da base oficial do Terraform antes de gerar a baseline semântica que alimenta o LiveCopilot.

## 2) CHECKLIST DE EXECUÇÃO
1. **source_policy** – validar a política oficial-first, registros de fontes e lotes aprovados.
2. **source_manifest** – listar arquivos, URLs e metadados que entram no corpus.
3. **corpus_freeze** – baixar e travar os artefatos originais com hashes controlados.
4. **parsing** – aplicar políticas de parsing e gerar `data/knowledge_parsed/terraform/`.
5. **chunking** – produzir chunks por heading e atualizar `docs/TERRAFORM_CHUNKING_METADATA.json`.
6. **lexical_validation** – rodar perguntas-chave contra o subset chunkado e registrar respostas.
7. **chunk_refinement** (quando necessário) – ajustar tamanho/títulos dos chunks que não respondem corretamente.
8. **semantic_baseline / embeddings** – concluído em 2026-03-18 no sandbox `data/semantic_index_experiments/terraform_pilot/`; rerodado em `20260318T190458Z` com cobertura semântica suficiente nos tópicos obrigatórios.
9. **semantic_refinement** (quando necessário) – concluído em `20260318T190458Z` com reforço de chunks para CLI, state/backend/workspaces e modules.
10. **final_report** – documentar achados, cobertura e gaps.
11. **final_handoff** – publicar handoff com orientações e próximos passos.
12. **STATUS atualizado** – registrar no `STATUS.md` o checkpoint desta rodada.
13. **pendências registradas** – listar bloqueios ou itens aguardando terceiros.

## 3) REGRA DE FECHAMENTO DA FRENTE
Enquanto `semantic_baseline` e `embeddings` não estiverem concluídos e validados, ou enquanto a baseline semântica mostrar cobertura insuficiente nos tópicos obrigatórios, a frente Terraform permanece com estado `closure_pending` e não pode ser marcada como `closed`, mesmo que os demais elementos anteriores do checklist estejam feitos. Com a rerodada `20260318T190458Z`, esse critério foi satisfeito para os tópicos obrigatórios do domínio.

## 4) ESTADO ATUAL DO TERRAFORM
- **estado:** `closed`
- **motivo:** após o refinement de chunks e a rerodada da baseline semântica em `20260318T190458Z`, os tópicos obrigatórios de CLI, state/backend/workspaces e modules ficaram semanticamente coerentes; permanece apenas uma observação residual no chunk definicional do AWS provider.
