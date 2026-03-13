# HANDOFF: Project Root Reorganization (20260312T220410Z)

## Estado anterior
- Root `/lab/projects` estava contaminado com artefatos operacionais do livecopilot/orquestrador (`AGENTS.md`, `queue/`, `results/`, `state/`, `codex_loop.sh`, backups, etc.).
- Projeto principal já existia em `/lab/projects/livecopilot`.

## Artefatos gerados
- `docs/coverage/projects_root_inventory_20260312T215756Z.json`
- `docs/coverage/projects_root_inventory_20260312T215756Z.txt`
- `docs/coverage/projects_root_classification_20260312T215756Z.json`
- `docs/coverage/projects_root_reorganization_plan_20260312T215756Z.json`
- `docs/coverage/projects_root_reorganization_execution_20260312T215756Z.json`

## Classificação
- pertence claramente ao livecopilot: 66 itens
- pertence claramente a outro projeto/shared: 2 itens (`.codex`, `.venv`)
- ambíguo/quarentena: 1 item (`.supervisor`)

## O que foi movido
- Movidos 66 itens de alta confiança de `/lab/projects` para `/lab/projects/livecopilot`.
- Conflitos no destino principal resolvidos conservadoramente para não sobrescrever:
  - `/lab/projects/README.md` -> `/lab/projects/livecopilot/_root_recovered_20260312T215756Z/README.md`
  - `/lab/projects/STATUS.md` -> `/lab/projects/livecopilot/_root_recovered_20260312T215756Z/STATUS.md`
  - `/lab/projects/logs` -> `/lab/projects/livecopilot/_root_recovered_20260312T215756Z/logs`
- Execução sem erro: `moved=66`, `errors=0`, `skipped_missing_source=0`.

## O que ficou pendente (não movido)
- `/lab/projects/.codex` (classificado como shared/tooling)
- `/lab/projects/.venv` (classificado como shared/outro)
- `/lab/projects/.supervisor` (ambíguo; preservado por segurança)

## Validação pós-reorganização
- Estrutura mínima confirmada em `/lab/projects/livecopilot`:
  - `app/`, `docs/`, `scripts/`, `tests/`, `STATUS.md`, `README.md`, `queue/`, `results/`, `state/`, `logs/`, `loop`
- Teste mínimo executado:
  - `cd /lab/projects/livecopilot && ./scripts/unit_test_gate.sh`
  - Resultado: `Ran 191 tests` -> `OK`

## Causa raiz provável (com evidência)
- Evidência técnica em `codex_loop.sh`:
  - `ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`
  - `codex exec ... --cd "$ROOT_DIR" ...`
- Quando o script estava em `/lab/projects`, todo estado operacional era escrito no root errado.
- Evidência documental no README legado (agora em `_root_recovered_.../README.md`): instruções explícitas para `cd /lab/projects`.

## Prevenção recomendada
- Manter execução do loop exclusivamente em `/lab/projects/livecopilot`.
- Já aplicado nesta rodada:
  - atualização mínima do texto de uso do wrapper `loop` para path correto `/lab/projects/livecopilot/loop`.
- Opcional (próxima rodada): atualizar/arquivar README legado de orquestrador em `_root_recovered_...` para evitar confusão futura.

## Próximos passos sugeridos
1. Decidir destino definitivo de `.supervisor` (manter no root como estado de ferramenta ou consolidar no projeto).
2. Decidir se `.venv` raiz deve ser mantido, removido manualmente, ou reatribuído para outro fluxo.
3. (Opcional) Criar um pequeno guard no `codex_loop.sh` para avisar/abortar se `ROOT_DIR` não for `/lab/projects/livecopilot`.
