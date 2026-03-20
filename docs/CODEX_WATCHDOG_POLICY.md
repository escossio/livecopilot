# CODEX WATCHDOG POLICY

Este documento define os guardrails operacionais do Codex no projeto LiveCopilot.

---

## OBJETIVO

Evitar execução fora do escopo, alterações excessivas e regressões causadas por sessões longas ou instruções ambíguas.

---

## GATILHOS DO WATCHDOG

O watchdog deve disparar alerta quando houver:

1. alteração fora do escopo declarado
2. alteração em muitos arquivos
3. alteração em arquivos críticos
4. instrução com múltiplos domínios misturados

---

## LIMITE SEGURO

Sem confirmação, o limite seguro é:

- até 5 arquivos modificados

Acima disso, responder com:

WATCHDOG ALERT

---

## ARQUIVOS CRÍTICOS

- app/services/knowledge_search.py
- app/services/suggestions.py
- app/services/transcription.py
- app/services/infra_status_connector.py
- app/services/knowledge_parsers.py
- app/services/knowledge_tags.py
- app/api/routes.py

Mudanças nesses arquivos exigem confirmação.

---

## COMPORTAMENTO

Se o watchdog disparar:

- não executar imediatamente
- listar o motivo do alerta
- mostrar arquivos afetados ou conflito de escopo
- solicitar confirmação antes de continuar
