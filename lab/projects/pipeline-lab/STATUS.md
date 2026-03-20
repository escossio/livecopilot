## Checkpoint 2026-03-18: Pipeline Lab disponível para teste manual
- Objetivo desta rodada:
  - montar rapidamente o servidor HTTP para API (`uvicorn app.main:app`) e a UI (`python3 -m http.server`) para que o piloto possa validar o cockpit e o endpoint `/api/runs`.
- Comandos usados:
  - API: `. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - UI: `python3 -m http.server 8090 --directory web`
  - (local env) `curl http://127.0.0.1:8000/api/runs`
- URLs acessíveis:
  - API: `http://127.0.0.1:8000/api`
  - UI: `http://127.0.0.1:8090/`
- Validações executadas:
  - `curl http://127.0.0.1:8000/api/runs` (listagem JSON)
  - `curl http://127.0.0.1:8090` (HTML da UI)
- Primeiro domínio recomendado para testes manuais: `terraform` (já possui run completa e artefatos que o cockpit exibe).
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_TEST_ACCESS_20260318T030611Z.md`

## Checkpoint 2026-03-18: Pipeline Lab acessível e com start script
- Objetivo desta rodada:
  - eliminar o erro `ERR_CONNECTION_REFUSED` em 10.45.0.3:8000/8090 iniciando API e UI em 0.0.0.0 e ensinando um comando único para subir os dois serviços.
- Causa identificada:
  - nada estava escutando nas portas 8000/8090, portanto o navegador/móvel não chegava a conectar.
- Comandos finais usados:
  - `. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - `python3 -m http.server 8090 --bind 0.0.0.0 --directory web`
- Scripts criados:
  - `scripts/start-pipeline-lab.sh` (usa `nohup`, log em `/tmp`, imprime PIDs e URLs)
  - `scripts/status-pipeline-lab.sh` (mostra listeners, PIDs e códigos HTTP para API/UI)
- Validações locais:
  - `curl http://127.0.0.1:8000/api/runs`
  - `curl http://127.0.0.1:8090`
- Validações via rede:
  - `curl http://10.45.0.3:8000/api/runs`
  - `curl http://10.45.0.3:8090`
  - `ss -tulnp | grep -E '8000|8090'` confirmou `0.0.0.0:8000` e `0.0.0.0:8090`
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_ACCESS_FIXED_20260318T031838Z.md`

## Checkpoint 2026-03-18: validação final do acesso
- Objetivo desta rodada:
  - confirmar que o script de start deixa API e UI escutando em 0.0.0.0/8000+8090 e que os endpoints respondem local e via IP.
- Novidades:
  - `scripts/start-pipeline-lab.sh` agora dispara `.venv/bin/python3 -m uvicorn` e `.venv/bin/python3 -m http.server` via `setsid`, garantindo background persistente.
- Comandos executados:
  - `bash scripts/start-pipeline-lab.sh`
  - `curl http://127.0.0.1:8000/api/runs`
  - `curl http://127.0.0.1:8090`
  - `curl http://10.45.0.3:8000/api/runs`
  - `curl http://10.45.0.3:8090`
  - `ss -tulnp | grep -E '8000|8090'`
- Documento gerado:
  - `docs/HANDOFF_PIPELINE_LAB_ACCESS_VALIDATION_20260318T033806Z.md`

## Checkpoint 2026-03-18: Pipeline Lab acessível em rede local
- Objetivo desta rodada:
  - garantir que a API e a UI escutem em 0.0.0.0 nas portas 8000/8090 e validar o acesso via 10.45.0.3 para testes no celular.
- Comandos usados:
  - `. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - `python3 -m http.server 8090 --bind 0.0.0.0 --directory web`
- Validações locais:
  - `curl http://127.0.0.1:8000/api/runs`
  - `curl http://127.0.0.1:8090`
- Validações via rede:
  - `curl http://10.45.0.3:8000/api/runs`
  - `curl http://10.45.0.3:8090`
- Portas confirmadas em `ss -tulnp`: API e UI ouvindo em 0.0.0.0.
- URLs finais para teste no celular:
  - API: `http://10.45.0.3:8000/api`
  - UI: `http://10.45.0.3:8090/`
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_NETWORK_ACCESS_20260318T031201Z.md`

## Checkpoint 2026-03-18: ergonomia do uso diário do Pipeline Lab
- Objetivo desta rodada:
  - deixar a UI espaço mais prática para operações humanas: criar runs, ver artifacts, entender o que deu certo ou falhou.
- Arquivos lidos:
  - `web/index.html`
  - `web/app.js`
  - `web/styles.css`
- Alteração aplicada:
  - painel “Runs” agora permite escolher domínio (terraform/python), dispara `POST /api/runs` e recarrega toda a lista após a criação.
  - card “Artifacts” mostra os arquivos gerados por cada stage (extraídos de `metadata.executed_stages`) e se mantém sincronizado ao trocar de run ou avançar stages.
  - mensagens de criação usam classes `success`/`error`/`neutral`, botões exibem loading/disabled e o cockpit atualiza o status das runs após cada operação.
- Conclusão técnica:
  - o cockpit passa a suportar criação de runs diretamente da UI, rastrear artifacts visíveis e dar feedback imediato, o que melhora a ergonomia diária antes de evoluir para runner/API robusta.
- Testes:
  - (documental, manual via navegador: criar run terraform, confirmar artefatos e mensagens)
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_DAILY_USE_IMPROVEMENTS_20260318T025513Z.md`

## Checkpoint 2026-03-18: operação next stage via UI/API
- Objetivo desta rodada:
  - permitir que o botão “Executar próximo stage” dispare o endpoint POST `/api/runs/{run_id}/next`, deixando a UI/API controlar o motor.
- Arquivos lidos:
  - `README.md`
  - `docs/PROJECT_SCOPE.md`
  - `docs/STAGE_GATES.md`
  - `app/api/routes.py`
  - `app/services/runner.py`
  - `runs/e1505998-bb3a-4f8e-8592-8e1d45f046ff/`
  - `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/`
  - `web/index.html`
  - `web/app.js`
  - `web/styles.css`
- Alteração aplicada:
  - POST `/api/runs/<id>/next` dispara o runner, aplica gate e retorna o payload atualizado
  - o botão “Executar próximo stage” chama esse endpoint, mostra loading/resultado e recarrega a run
  - o blocked python run e o terraform permitido foram usados para validar os fluxos
- Conclusão técnica:
  - a UI/API agora operam o motor do Pipeline Lab a partir do navegador, usando o gate existente; log/summary/artifacts continuam sendo a fonte de verdade.
- Testes:
  - (documental, clique manual + scripts `routes.execute_run_stage`)
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_NEXT_STAGE_UI_API_20260318T020000Z.md`

## Checkpoint 2026-03-18: stage gates mínimos implementados
- Objetivo desta rodada:
  - reforçar o runner com checagens de gates antes de executar cada stage e gravar bloqueios.
- Arquivos lidos:
  - `README.md`
  - `docs/EXECUTION_PROTOCOL.md`
  - `docs/STAGE_GATES.md`
  - `app/services/stage_gate.py`
  - `app/services/runner.py`
  - `web/app.js`
  - `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/`
- Alteração aplicada:
  - `StageGate.check` valida pré-requisitos (`source_policy`, `source_manifest`, `corpus_freeze`, `parsing`) antes de rodar um stage
  - o runner bloqueia o stage, registra `blocked` + motivo no summary/artifacts/log e não avança o pointer
  - handoff `docs/HANDOFF_PIPELINE_LAB_STAGE_GATES_20260318T015000Z.md` documenta o cenário permitido (parsing) e bloqueado (chunking sem parsing)
- Conclusão técnica:
  - o Pipeline Lab agora diferencia runs aprovadas vs. gates bloqueados e expõe essa informação na UI/API
- Testes:
  - (documental, `routes.execute_run_stage` permitindo `parsing` e bloqueando `chunking` após ajuste de stage)
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_STAGE_GATES_20260318T015000Z.md`

## Checkpoint 2026-03-18: primeira UI funcional do Pipeline Lab
- Objetivo desta rodada:
  - tornar visível e navegável o estado das runs via a nova interface minimalista em `web/`.
- Arquivos lidos:
  - `README.md`
  - `docs/PROJECT_SCOPE.md`
  - `docs/DAILY_USAGE.md`
  - `app/api/routes.py`
  - `app/services/runner.py`
  - `app/storage/runs_store.py`
  - `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/`
  - `web/index.html`
  - `web/app.js`
  - `web/styles.css`
- Alteração aplicada:
  - criados painel, log e histórico mínimos que consomem `GET /api/runs` e `GET /api/runs/:id` (com fallback) na tela do cockpit
  - reestilizado o layout para dividir lista, detalhes, histórico e log/summary
  - documentado emissões no handoff `docs/HANDOFF_PIPELINE_LAB_UI_MINIMUM_20260318T013500Z.md`
- Conclusão técnica:
  - a interface já mostra a run terraform, history com dois stages e log/summary; não há integração com o LiveCopilot nem backend HTTP completo ainda.
- Testes:
  - (documental, manual via navegador local)
- Documentação gerada:
  - `docs/HANDOFF_PIPELINE_LAB_UI_MINIMUM_20260318T013500Z.md`

Pipeline Lab project skeleton created

## Checkpoint 2026-03-18: primeira run operacional
- Domínio: terraform (providers_pending)
- Run ID: fd999231-3b52-42a8-96f6-2dc761cc9a71
- Etapa/status inicial gravados e summary em `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/summary.json`
- Armazenado log e artifacts mínimos
- API mínima (`app/api/routes.py`) respondeu ao `create_run` e `get_runs`

## Checkpoint 2026-03-18: primeira execução de stage
- Run ID: fd999231-3b52-42a8-96f6-2dc761cc9a71
- Stage: source_policy (status transicionou created → running → completed)
- Summary/log/artifacts atualizados em `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/`
- API mínima `app/api/routes.execute_run_stage` garantiu a exposição do novo estado

## Checkpoint 2026-03-18: primeira execução encadeada de stages
- Run ID: fd999231-3b52-42a8-96f6-2dc761cc9a71
- Stages executados: `source_policy` e `source_manifest`
- Status/RUN atualizado em `app/storage/runs.json` e artefatos/log/summary em `runs/fd999231-3b52-42a8-96f6-2dc761cc9a71/`
- API `app/api/routes.execute_run_stage` expõe o pipeline encadeado

## Checkpoint 2026-03-18: primeira execução real com artifact
- Run ID: fd999231-3b52-42a8-96f6-2dc761cc9a71 (terraform)
- Stage executado: `corpus_freeze` (artifact real gerado em `runs/.../stage_artifact_corpus_freeze.md`)
- artifacts.json e summary.json registram o artifact e o history ampliado
- UI mínima continua mostrando a run, histórico e summary atualizados
