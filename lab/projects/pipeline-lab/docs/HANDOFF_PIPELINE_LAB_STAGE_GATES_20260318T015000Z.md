# Handoff Pipeline Lab — stage gates mínimos

## Gates implementados
- `source_manifest` exige que `source_policy` conste no histórico de execuções.
- `corpus_freeze` só roda se `source_manifest` já foi executado.
- `parsing` exige `corpus_freeze`.
- `chunking` depende de `parsing`.
- O runner consulta `StageGate.check` antes de executar cada etapa e grava o resultado (allowed + reason).

## Cenário permitido validado
- Run `fd999231-3b52-42a8-96f6-2dc761cc9a71` (domínio `terraform`) executou `corpus_freeze` e depois `parsing`, ambos com gate aprovado. Os artifacts foram persistidos e o status continuou `completed` com o próximo stage apontando para `chunking`.

## Cenário bloqueado validado
- Nova run `e1505998-bb3a-4f8e-8592-8e1d45f046ff` (domínio `python`) tentou executar `chunking` sem o gatilho `parsing`; o gate retornou `allowed=false` e a run foi marcada `blocked`, com log e summary registrando o bloqueio e o motivo.

## Impacto no runner/API/UI
- O runner agora registra quando um gate é bloqueado (summary.gate, artifacts/log com flag `blocked`).
- O status `blocked` permanece na run e a UI mínima reflete a cor/razão via `summary.result` e `status-pill` class.
- A API (`routes.execute_run_stage`) retorna o estado atualizado com `final_status` e `gate` para permitir supervisão.

## Próximos passos sugeridos
- expandir o gate para as etapas seguintes (e.g., `chunking` → `lexical_validation`).
- permitir mensagem de alerta na UI quando um run estiver blocked.
- criar mecanismo de reintento/descrição dos passos pendentes para desbloquear o gate.
