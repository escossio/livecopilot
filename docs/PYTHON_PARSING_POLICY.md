# Política de Parsing — Corpus Python (2026-03-17T05:00:00Z)

## Objetivo
- garantir que o corpus bruto do Lote 1 seja limpo de ruído de interface (navs, sidebars, footers) seguindo o mesmo rigor oficial-first aplicado nas etapas anteriores.
- produzir HTML parseado que preserve títulos, seções, assinaturas e blocos explicativos úteis às futuras etapas de chunking sem ainda gerar embeddings.

## Regras de parsing aplicadas
1. partir das páginas congeladas (`data/knowledge_raw/python/`) e manter apenas o conteúdo do `<div id="content">`, ou o bloco `.document` quando o `id` não estiver presente.
2. remover completamente os elementos de navegação (`nav`, `header`, `footer`, `aside`, menus, breadcrumbs e sidebars identificados como `sidebar`, `sphinxsidebar`, `related`, `sphinxsidebarwrapper` ou `rstd-navigation`).
3. eliminar `<script>` e `<style>` para evitar carregar comportamento ou estilos que não interessam à ingestão.
4. preservar títulos (`h1`, `h2`, `h3`), parágrafos, listas, blocos de código curtos, assinaturas de funções e descrições principais, garantindo que o conteúdo parseado mantenha a identidade do tópico.
5. descartar `div` ou `span` vazios após a limpeza para evitar poluição sem conteúdo.
6. registrar as páginas parseadas em `data/knowledge_parsed/python/` mantendo a mesma hierarquia usada no corpus bruto.

## Observações
- Esse parsing é controlado; não há chunking ou indexação na Etapa 4.
- As amostras antes/depois (relatório `docs/PYTHON_PARSING_SAMPLE_REPORT_*.md`) documentam o impacto da limpeza em alguns arquivos-chave.
- Qualquer recaptura do corpus deve reaplicar essa política antes de regenerar os artefatos derivados.
