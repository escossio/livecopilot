# Handoff LiveCopilot Terraform Parsing (2026-03-17T21:55:00Z)

## Contexto
- após congelar o corpus bruto do Lote 1 (CLI, linguagem, state/backends/workspaces), iniciamos a Etapa 4 para fazer parsing/limpeza controlada antes do chunking.  
- os artefatos brutos ainda residem em `data/knowledge_raw/terraform/`; o parsing produz uma réplica limpa em `data/knowledge_parsed/terraform/`.

## Ações realizadas
1. aplicamos a política de parsing (remover nav, header, footer, scripts, sidebars e classes de navegação) e mantivemos títulos, descrições e exemplos de CLI/HCL.  
2. geramos as versões parseadas das três páginas congeladas (CLI, language, backends) e salvamos as saídas em `data/knowledge_parsed/terraform/{cli,language,state}`.  
3. documentamos a política (`docs/TERRAFORM_PARSING_POLICY.md`) e coletamos amostras antes/depois (`docs/TERRAFORM_PARSING_SAMPLE_REPORT_20260317T215000Z.md`).

## Estado final do corpus
- `data/knowledge_parsed/terraform/` contém os HTMLs limpos; cada família tem um arquivo parseado pronto para chunking.  
- Amostras registram o que foi removido (navegação/menus) e o que foi preservado (heads, exemplos).  
- O desk agora pode definir a bateria de perguntas e avançar para chunking controlado do Lote 1.

## Próximos passos sugeridos
1. validar o conteúdo parseado e liberar o Lote 1 para chunking (Etapa 5).  
2. manter o lockfile e a política alinhados enquanto os próximos lotes forem congelados.  
3. iterar a bateria de perguntas inspirada em C/Python para orientar a chunking do Terraform.
