# Regras do projeto

## Fluxo
- Antes de qualquer alteracao, ler os arquivos relevantes.
- Sempre consultar `STATUS.md` antes de continuar uma tarefa ja iniciada.
- Ao concluir uma etapa, registrar checkpoint em `STATUS.md`.

## Alteracoes
- Fazer a menor mudanca possivel para resolver o problema.
- Nao reorganizar arquivos sem necessidade explicita.
- Nao introduzir dependencias novas sem necessidade real.
- Nao sobrescrever arquivo existente sem backup quando ele for estrutural para o projeto.

## Resposta
- Informar objetivamente: o que foi lido, o que foi alterado, o que falta.
- Se houver comandos para validacao, listar ao final.

## Orquestrador Local
- O orquestrador usa contexto persistente em `AGENTS.md`, `project_state.md` e `queue/next.md`.
- O loop deve executar no maximo uma tarefa por chamada.
- O loop deve parar quando houver risco, ambiguidade ou necessidade clara de aprovacao humana.
- Logs, resultados e estado devem ficar legiveis por terminal simples.

## Contrato Operacional do Codex
- Sempre que o loop montar um prompt para o Codex, ele deve pedir uma saida final curta e auditavel.
- A saida final ideal deve conter:
  - `status final`
  - `comandos executados`
  - `arquivos tocados`
  - `o que foi alterado`
  - `o que falta`
  - `se precisa aprovacao`
  - `se houve erro`
