# Handoff Pipeline Lab — botão "Próximo Stage"

## Endpoint next stage implementado
- POST `/api/runs/{run_id}/next` dispara `runner.execute_stage`, que já aplica stage gate e atualiza summary/log/artifacts.
- Retorna o payload atualizado da run (status, gate, artifact) para a UI.

## Ação na UI implementada
- Botão “Executar próximo stage” no painel de detalhes (`web/index.html`) aciona o novo endpoint.
- O botão fica em loading enquanto a chamada acontece, mostra mensagem de progresso e exibe o resultado ou erro.
- O status da run aparece com badge verde/vermelho/âmbar conforme `summary.final_status` (`success`, `blocked`, `warning`).

## Fluxo permitido validado
- Run `fd999231-3b52-42a8-96f6-2dc761cc9a71` (terraform) avançou de `parsing` para `chunking` via botão; o gate validou `corpus_freeze`, os artifacts/log/summary foram atualizados e a UI recarregou os dados com novo artifact.

## Fluxo bloqueado validado
- Run `e1505998-bb3a-4f8e-8592-8e1d45f046ff` (python) tentou avançar o stage `chunking` sem `parsing`; o gate respondeu `allowed=false`, a run foi marcada `blocked`, log/summary/artifacts registraram o motivo e o botão exibiu `bloqueado`.

## Limitações atuais
- O backend HTTP não está completo, então a UI depende de fetch que pode falhar; há fallback com run hardcoded.
- Não há autorização ou confirmação por etapa, apenas o botão simples.
- O botão não faz retry automático quando um gate ainda aguarda uma etapa ausente.

## Próximos passos sugeridos
- publicar um servidor mínimo (Flask/FastAPI) que sirva `/api/runs` e `/api/runs/{id}/next` aproximando o CLI real.
- conectar o botão a um indicador de progresso visual e permitir cancelar se uma execução demorar.
- registrar métricas de duração de gate e adicionar auditoria de bloqueios para supervisores.
