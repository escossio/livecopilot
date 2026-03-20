# CODEX EXECUTION CONTRACT

Este documento define o contrato obrigatório para execução de instruções.

---

## CAMPOS OBRIGATÓRIOS

Toda instrução deve conter:

- MODELO_RECOMENDADO
- JUSTIFICATIVA_DO_MODELO
- OBJETIVO
- ESCOPO
- NAO_FAZER
- ENTRADAS
- PASSOS
- VALIDACAO
- ARTEFATOS_ESPERADOS
- CRITERIO_DE_PARADA
- ENTREGA_FINAL
- ARQUIVOS_DE_CONTEXTO

---

## REGRA

Se algum campo estiver ausente:

Responder:

PRE-RUN CHECK FAILED

Listar campos faltantes e solicitar correção.

---

## POLÍTICA DE MODELO

mini → tarefas mecânicas  
modelo maior → arquitetura e semântica

---

## REGRA DE FECHAMENTO DE FRENTE

`closure_decision` MUST NOT EXECUTE IF ANY REQUIRED ARTIFACT IS MISSING OR DIVERGENT.

Antes de qualquer `closure_decision`, a frente deve passar por `python3 scripts/front_closure_precheck.py <FRONT>` e receber `PRECHECK PASSED`.
Se o precheck falhar, o fechamento fica bloqueado e a execução deve parar até autorização explícita do operador.

### Uso rápido

```bash
python3 scripts/front_closure_precheck.py MACHINE_LEARNING
```

- `PRECHECK PASSED` → o fechamento está elegível para a etapa seguinte.
- `PRECHECK FAILED: ...` → requisito obrigatório ausente/divergente; `closure_decision` bloqueado.
