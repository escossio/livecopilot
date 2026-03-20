# CODEX MODEL POLICY

Este documento define a política de escolha de modelo para o uso do Codex no projeto LiveCopilot.

---

## OBJETIVO

Reduzir consumo desnecessário e manter disciplina operacional na escolha do modelo.

---

## REGRA GERAL

### Usar modelo MINI para:
- leitura de arquivos
- inventário
- geração de relatórios
- reruns
- testes
- documentação
- ingestão mecânica
- tarefas repetitivas
- ajustes pequenos e localizados

### Usar modelo maior para:
- arquitetura
- debugging complexo
- ranking semântico
- retrieval
- chunking
- refatorações sensíveis
- mudanças em arquivos críticos
- decisões com alto risco de regressão

---

## REGRA DE VALIDAÇÃO

Toda instrução deve conter:

- MODELO_RECOMENDADO
- JUSTIFICATIVA_DO_MODELO

Antes de executar, o Codex deve comparar:

- modelo recomendado
- modelo ativo

Se houver divergência, responder:

MODEL POLICY WARNING

Modelo recomendado: X
Modelo ativo: Y

Solicitar confirmação antes de continuar.
