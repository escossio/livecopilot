# Handoff Pipeline Lab — ergonomia diária

## Criação de run via UI
- Painel "Runs" agora tem seletor de domínio (terraform/python), botão “Criar run” e mensagem de status.
- O botão dispara `POST /api/runs` com o domínio selecionado, atualiza a lista completa (`/api/runs`) e seleciona a run criada.
- Há bloqueio de UI/feedback (disabled + texto) durante a chamada e mensagens verdes/vermelhas ao final.

## Exibição de artifacts
- Card “Artifacts” lista os artifacts produzidos por cada stage (extraídos de `metadata.executed_stages`).
- Cada item mostra o stage e o nome do arquivo, facilitando abrir/copiar o path gerado em `runs/<run_id>/`.
- O card atualiza automaticamente ao selecionar run nova ou ao avançar stages.

## Melhorias de feedback visual
- Mensagens de criação adotam classes `success`/`error`/`neutral` e cores dedicadas para clareza.
- Botões mostram loading (texto) e ficam desabilitados durante chamadas importantes.
- A UX do cockpit ficou mais transparente ao recarregar runs após operações e indicar claramente o que falhou.

## Próximos passos sugeridos
- registrar artefatos em um endpoint (`/api/runs/{id}/artifacts`) para permitir download direto.
- manter inventário local de domains disponíveis para alimentar o seletor dinamicamente.
- juntar os feedbacks a um log de auditoria/alerta para supervisores do Pipeline Lab.
