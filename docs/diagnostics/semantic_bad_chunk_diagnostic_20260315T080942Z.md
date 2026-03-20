# Semantic bad chunk diagnostic (20260315T080942Z)

## Objetivo
- confirmar que os parciais remanescentes continuam vindo de chunks com perfil estrutural ruim (front matter, metadata, aliases, caminhos, etc.).
- registrar os sinais usados pelo detector de ruído e preparar o ajuste de ranking para penalizar esses candidatos antes da síntese final.

## Definição de chunk estruturalmente ruim
- **Front matter YAML** (`---` no início com `title`, `description`, `keywords`, `page_title`, `canonical`, `reviewer`, `sort_rank` etc.).  
- **Aliases/paths** que apenas listam rotas (`/docs/...`, `/notification-policies/...`, `/engine/security/trust/...`).  
- **Keywords** e `description` no início do trecho antes da primeira frase útil.  
- **Breadcrumbs, reviewer/header ou metadata automatizada** (`# START AUTO GENERATED METADATA`, `reviewer:`).  
- **Introduções documentais ou headings excessivos** que não respondem diretamente à pergunta.

Esses sinais são combinados em `STRUCTURAL_NOISE_PATTERNS` dentro de `app/services/knowledge_search.py` e somam até `0.6` de penalidade por chunk, garantindo que o conteúdo útil seja priorizado.

## Resultados do diagnóstico
- A tabela de rastreio em `docs/diagnostics/semantic_bad_chunk_trace_20260315T080942Z.json` mostra que, após o ajuste, 9 dos 10 top chunks ainda são `noise` (front matter) e recebem penalidade de `0.28–0.6`.  
- O único chunk que permanecia bom (`Quando usar modulos no Terraform?`) resta alinhado (`chunk_type=use`, `noise_penalty=0.0`).  
- O filtro ainda não converteu nenhum parcial em coerente, mas garantiu que os chunks com metadata pesada não subam sem narrativa útil.

## Próximo passo
- usar o histórico gerado para comparar `before/after` nos testes distribuídos e decidir se é necessário remover esses chunks (“exclusão controlada”) ou apenas mantê-los penalizados até surgirem alternativas mais limpas.
