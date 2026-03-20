# Handoff LiveCopilot Terraform Source Policy (2026-03-17T20:30:00Z)

## Contexto
- após os pilotos C e Python comprovarem o modelo official-first, precisamos abrir uma nova frente para Terraform sem contaminar o índice global.
- esta rodada é documental: definimos escopo e política de fontes antes de qualquer freeze/parsing.

## Ações realizadas
1. revisamos os relatos finais dos pilotos C e Python (`docs/C_PILOT_FINAL_REPORT.md`, `docs/PYTHON_DOMAIN_FINAL_REPORT.md`) e a disciplina oficial-first (`docs/PROJECT_BRAIN.md`, `docs/INGESTAO_C_EXECUTION_PLAN.md`).
2. definimos um recorte inicial controlado (linguagem, CLI, estado, modules, providers AWS/Azure/Google, workspaces, plan/apply/destroy) e justificamos por que não ingerimos o Terraform inteiro logo de cara.
3. catalogamos fontes candidatas em `docs/TERRAFORM_OFFICIAL_SOURCE_POLICY.md`, classificando-as em FONTE_PRIMARIA (docs oficiais CLI/linguagem/Registry/backends/modules), FONTE_SECUNDARIA (HashiCorp Learn, release notes, guias de Terraform Cloud) e NAO_PRIORIZAR_AGORA (blogs, StackOverflow, cursos, repositórios não oficiais).
4. registramos o que entra/agora e o que fica de fora, além dos riscos e próximos passos para o manifesto e o congelamento.

## Estado final
- política oficial registrada em `docs/TERRAFORM_OFFICIAL_SOURCE_POLICY.md`.  
- escopo inicial aprovado (linguagem, CLI, state, backends, modules, providers prioritários).  
- team pronto para a próxima etapa (manifesto operacional) sem tocar no índice global.

## Próximos passos sugeridos
1. montar manifesto de fontes com lotes e hashes oficiais (Etapa 1).  
2. congelar o subset Terraform aprovado somente após manifesto verificado (Etapa 2).  
3. definir bateria de perguntas iniciais inspirada em C/Python para orientar chunking e validação lexical.
