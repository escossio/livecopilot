# Terraform parsing policy — 2026-03-17T21:50:00Z

## Objetivo
- transformar os HTMLs do Lote 1 em uma camada limpa antes de chunking.

## Regras de limpeza
- remover blocos `nav`, `header`, `footer`, `aside` e formulários de navegação.
- remover `script`, `style`, `noscript` e `link` de cabeçalho.
- remover blocos com classes/breadcrumbs de navegação (`*nav*`, `*breadcrumb*`, `*sidebar*`).
- preservar títulos (`h1`–`h4`), descrições, exemplos de CLI/HCL, código em destaque e tabelas.
- manter o fluxo textual central e exemplos executáveis para facilitar chunking.

## Processo
- ler cada HTML congelado do Lote 1, aplicar a limpeza acima e salvar o HTML resultante em `data/knowledge_parsed/terraform/<familia>`.
- o corpus parseado deve manter <main>/<body> limpo com o conteúdo útil e sem menus.

## Validação
- revisar amostras antes/depois (`docs/TERRAFORM_PARSING_SAMPLE_REPORT_*.md`) para garantir que o conteúdo principal permaneça e a navegação foi removida.
