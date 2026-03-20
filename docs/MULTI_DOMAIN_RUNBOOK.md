# Multi-domain Runbook

## Objetivo do runbook
Este documento não descreve um processo novo: ele organiza o pipeline já validado para C, Python e Terraform nas mesmas etapas que foram comprovadas no projeto. Com este runbook podemos registrar e gerenciar a execução sequencial de vários domínios usando a mesma cadeia de fases que funcionou até agora.

## Ordem oficial das etapas
1. `source_policy`
2. `source_manifest`
3. `corpus_freeze`
4. `parsing`
5. `chunking`
6. `lexical_validation`
7. `chunk_refinement`
8. `semantic_baseline`
9. `semantic_refinement`
10. `domain_closure`

Cada etapa deve ser conduzida em sequência e finalizada antes de iniciar a próxima para qualquer domínio.

## Fila de domínios
- **C** — concluído
- **Python** — concluído
- **Terraform** — em andamento
- **Linux** — candidato futuro
- **Docker** — candidato futuro

A fila é apenas um exemplo de ordem de atendimento; novos domínios devem ser inseridos no final e atualizados conforme progridem.

## Regras de execução
- Executar apenas um domínio por vez até que todas as etapas do pipeline sejam concluídas ou documentadas como divergentes.
- Não pular etapas: cada domínio deve passar por todas as fases listadas em `Ordem oficial das etapas` na sequência correta.
- Não recriar artefatos existentes: use o histórico de freeze, parsing e chunking já registrado, mantendo consistência.
- Registrar divergências assim que surgirem (veja a seção `Tratamento de divergências`).
- Gerar o resumo final usando o template multi-domínio como última atividade de cada rodada.

## Tratamento de divergências
Quando houver diferença entre o esperado e o alcançado, use o seguinte formato mínimo para documentar:

| Campo | Descrição |
| --- | --- |
| **Domain** | Nome do domínio afetado |
| **Stage** | Nome da etapa em que ocorreu a divergência |
| **Status** | Ex.: `bloqueado`, `parcial`, `resolvido` |
| **Symptom** | Sintoma observado (ex.: chunks incompletos, parsing falhou) |
| **Probable cause** | Causa investigada ou hipótese mais provável |
| **Suggested action** | Próximo passo ou mitigação recomendada |

Divergências devem ser registradas antes de passar para o próximo domínio ou etapa subsequente.

## Resumo final obrigatório
Toda rodada multi-assunto termina com um resumo preenchido segundo o template `docs/MULTI_DOMAIN_EXECUTION_SUMMARY_TEMPLATE.md`. O resumo deve listar domínios processados, etapas alcançadas, artefatos entregues, divergências e ações recomendadas, além de um status final do lote.
