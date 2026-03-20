# AZURE Lexical Baseline Report

## Objetivo
- Validar se as consultas representativas de rede, storage, identidade e CLI apontam para chunks do domínio AZURE.

## Resultados

### 1. Query: `azure virtual machine networking`
- **Top1:** `azure_networking_documentation-0002-b2214c93fb7b3d0d` (`azure_networking_documentation.html`, score 65)
- **Top3:** включ. `azure_architecture_center-0002-...` (score 37), `azure_compute_documentation-0002-...` (score 31)
- **Domínio correto:** AZURE (todos os chunks pertencem à frente `azure`)

### 2. Query: `azure storage account types`
- **Top1:** `azure_storage_documentation-0002-3596c49a4c2f6cb4` (`azure_storage_documentation.html`, score 51)
- **Top3:** `azure_networking_documentation-0002-...` (49), `azure_architecture_center-0002-...` (32)
- **Domínio correto:** AZURE

### 3. Query: `azure identity managed identities`
- **Top1:** `azure_networking_documentation-0002-b2214c93fb7b3d0d` (`azure_networking_documentation.html`, score 49)
- **Top3:** `azure_architecture_center-0002-...` (36), `azure_storage_documentation-0002-...` (27)
- **Domínio correto:** AZURE

### 4. Query: `azure cli login command`
- **Top1:** `azure_networking_documentation-0002-b2214c93fb7b3d0d` (`azure_networking_documentation.html`, score 49)
- **Top3:** `azure_cli_documentation-0002-e903dbbf3f1d194e` (37), `azure_architecture_center-0002-...` (32)
- **Domínio correto:** AZURE

## Observações
- Todos os top3 retornos são provenientes de chunks da frente AZURE, confirmando o foco do baseline lexical.
