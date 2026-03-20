# Handoff – Chunking diagnostic (2026-03-15T20:27:28Z)

## Motivation
- Investigate por que as respostas ainda saem **parcialmente coerentes** nos tópicos de Terraform, Docker e Grafana mesmo com retrieval e ranking ajustados.
- Confirmar se o gargalo restante está no chunking/ingestão (front matter, metadata, headers) ou se os blocos úteis simplesmente não existem.

## Perguntas auditadas
- O que é um workspace no Terraform?
- Quando usar módulos no Terraform?
- O que é o host network driver no Docker?
- Para que serve o modo rootless no Docker?
- O que é content trust no Docker?
- O que é uma notification policy no Grafana Alerting?

## Achados por pergunta
- **Workspace**: o chunk útil existe (rank 2, `TRECHO_UTIL_USO`, score 0.633), mas o chunk front matter que abre o documento (score 0.643) impede que a definição suba primeiro.
- **Módulos**: o ranking já retorna de cara um chunk `TRECHO_UTIL_USO`, portanto didaticamente saudável.
- **Host network driver**: os dez primeiros hits são todos YAML/alias metadata (`FRONT_MATTER`, `noise`). A explicação prática (“If you use the `host` network mode…”) está no mesmo chunk, mas o metadata que precede essa frase domina a similaridade.
- **Rootless mode**: idem ao host network driver; o chunk inicia com metadata e só depois descreve o uso (Rootless executando em user namespace), e os blocos metadata superam o trecho útil (diferença >0.23 em similaridade).
- **Content trust**: o YAML `description/keywords/aliases` ocupa os primeiros seis resultados; apenas após isso aparece um bloco textual (score 0.425) – mas a explicação segue oculta enquanto o metadata for sempre o início do chunk.
- **Notification policy**: os chunks retornados são aliases e canonical URLs; o primeiro texto de instrução aparece apenas no rank 3 e carrega classificação `MISTO`.

## Conclusão geral
- O conteúdo existe nos documentos, mas a ingestão preserva o front matter/aliases no começo de cada chunk. Como a busca usa somente os primeiros 180 caracteres para construir o snippet, o ranking está sendo guiado unicamente pelos metadados e descarta o parágrafo útil que vem logo depois.

## Próxima ação sugerida
- Atualizar o chunker para pular o front matter (ou gerar chunks separados: metadados vs. corpo) e para penalizar mais agressivamente os blocos que são apenas aliases/redirecionamentos antes de atingir o conteúdo desejado. Mantemos a análise manual até que esse novo corte possa ser testado.

## Artefatos entregues
- `docs/diagnostics/chunk_quality_audit_20260315T202728Z.json`
- `docs/diagnostics/chunk_quality_audit_20260315T202728Z.md`
- `docs/diagnostics/chunk_source_comparison_20260315T202728Z.md`
- `docs/diagnostics/chunk_quality_summary_20260315T202728Z.md`
