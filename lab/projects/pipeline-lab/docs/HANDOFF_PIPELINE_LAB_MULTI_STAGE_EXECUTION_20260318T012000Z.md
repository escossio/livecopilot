# Handoff Pipeline Lab — execução encadeada de stages

## Run utilizada
- ID: fd999231-3b52-42a8-96f6-2dc761cc9a71
- Domínio: `terraform`

## Stages executados
1. `source_policy`
2. `source_manifest`

## Progressão registrada
- Status transitou de `created` → `running` → `completed` para cada stage com metadata atualizada em `app/storage/runs.json`
- `runs/.../summary.json` agora contém histórico completo (`history` com dois registros)
- `runs/.../artifacts.json` e `log.txt` refletem os dois eventos

## O que já funciona
- O runner determina o próximo stage no pipeline oficial e o grava antes/depois
- A API `execute_run_stage` pode ser chamada repetidamente para avançar stages
- O metadata guarda `executed_stages` e `last_executed_stage` para supervisão futura

## Próximos passos sugeridos
- adicionar gatilhos reais (gatestone checks) para cada stage + validações
- exibir o histórico de `executed_stages` em um dashboard simples
- suportar rollback/parada caso um stage falhe (status `blocked`)
