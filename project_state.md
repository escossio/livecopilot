# Estado do projeto

## Objetivo desta camada
- Reduzir o ciclo manual entre ChatGPT e Codex CLI com um loop local semiautonomo e auditavel.

## Baseline atual
- O orquestrador roda uma tarefa por execucao.
- O contexto persistente minimo fica em:
  - `AGENTS.md`
  - `project_state.md`
  - `queue/next.md`
- O loop salva:
  - prompt consolidado em `state/last_prompt.md`
  - ultimo resumo em `state/last_result.md`
  - estado vivo em `state/loop_status.json`
  - log bruto por execucao em `logs/`
  - resumo operacional por execucao em `results/`

## Politica de pausa
- Pausar quando houver sinal de risco, ambiguidade ou decisao humana.
- Criar `state/needs_approval.flag` quando o log ou resumo contiver sinais de risco.

## Estado operacional atual
- Estrutura v2 do orquestrador: pronta
- Modo seguro inicial: `--dry-run`
- Dry-run validado em dois cenarios:
  - tarefa simples sem risco, com arquivamento
  - tarefa com sinal de risco, com pausa por aprovacao
- Proxima evolucao esperada:
  - validar tarefas reais em modo nao interativo
  - manter o loop de uma unica iteracao por execucao
