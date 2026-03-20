# Terraform chunking policy — 2026-03-17T22:10:00Z

## Objetivo
- extrair trechos respondíveis do corpus parseado do Lote 1 antes de aplicar qualquer embedding ou persistência vetorial.

## Estratégia geral
- chunking por segmento lógico: cada seção (indicada por headings `h1`-`h3`) ou grupo textual coerente vira um chunk com título e conteúdo.  
- buscamos equilíbrio: chunks grandes o suficiente para preservar contexto (ex: descrição + exemplos + tabelas) e não tão longos que fiquem incontroláveis; descartamos blocos vazios/ruidosos.  
- cada chunk recebe metadados de `source_family`, `source_file`, `title/section`, `chunk_id`, `path` e `length` para rastreio.

## Política por família
- **CLI**: chunk por comando ou seção operacional (ex: `apply`, `plan`, `init`), mantendo exemplos de flags e saídas.  
- **Language**: chunka por conceito (variables, outputs, expressions, modules) e por blocos sintáticos definidores da HCL.  
- **State/backends/workspaces**: chunk por blocos explicativos sobre state storage, locking e workspaces, preservando notas de configuração e uso.

## Processos de chunking
1. percorremos o `<body>` do HTML parseado e iniciamos um novo chunk sempre que aparece um heading (`h1`-`h3`).  
2. acumulamos textos de parágrafos, sections, pré-formatados e tabelas até o próximo heading.  
3. salvamos o chunk como JSON em `data/knowledge_chunks/terraform/<familia>/terraform-<familia>-###.json`.  
4. mantemos chucks de amostras em `docs/TERRAFORM_CHUNKING_SAMPLE_REPORT_*.md` para revisão manual.

## Validação
- revisar as amostras documentadas e o arquivo de metadados (`docs/TERRAFORM_CHUNKING_METADATA.json`) para garantir que cada chunk tem título, seção e tamanho razoável.  
- o chunking deste piloto é limitado ao Lote 1; futuros lotes devem seguir as mesmas regras adaptadas às novas families.
