# Continuity Automation (Integracao Minima)

## Objetivo
Automatizar de forma minima e reversivel a captura de continuidade ao final de uma rodada, mantendo o fluxo manual existente.

## Comando padrao do operador (adotado)
- `scripts/round` passa a ser o entrypoint preferencial da rodada.
- `scripts/round` delega para `scripts/run_real_round_flow.sh`.
- se `--mode` nao for informado, assume `--mode run-once`.
- se flags de hook nao forem informadas, `scripts/round` agora assume:
  - `--enable-continuity-hook`
  - `--enable-embedding-maintenance`
- compatibilidade preservada: `scripts/run_real_round_flow.sh` continua funcional e suportado.

## Componentes
- `scripts/round`
  - launcher oficial do operador para rodada real.
- `scripts/continuity_build_payload.py`
  - gera payload canonico JSON por rodada.
- `scripts/run_continuity_capture.sh`
  - wrapper semi-automatico que gera payload e chama `continuity_ingest.py`.
- `scripts/run_round_closeout.sh`
  - ponto de integracao opcional no encerramento operacional da rodada.
- `docs/continuity/payloads/`
  - armazenamento auditavel dos payloads gerados.
- `docs/continuity/FACTS_CONTRACT.md`
  - contrato canonico de facts explicitos.

## Payload canonico gerado
Campos obrigatorios:
- `project_name`
- `session_id`
- `actor`
- `run_type`
- `summary_short`
- `summary_full`
- `status_md_path`
- `checkpoint_path`
- `facts[]`

Campos adicionados automaticamente:
- `run_key` deterministico (hash canonico dos campos da rodada + facts)

## Run key deterministico
Logica:
- normalizar campos de texto (trim + colapso de espacos)
- serializar payload canonico (ordenacao de chaves)
- hash SHA-256
- formato final: `run_<24 hex>`

Resultado:
- reexecucao com mesmo conteudo gera mesmo `run_key`
- ingestao fica idempotente por `UNIQUE (run_key)`

## Facts explicitos (enriquecimento)
Entrada recomendada:
- `--facts-file docs/continuity/examples/sample_facts.json`

Entrada opcional:
- `--fact-inline "fact_type|fact_status|title|body|component|priority|source_path|source_section"`

Exemplo com facts-file:
```bash
./scripts/run_continuity_capture.sh \
  --session-id agent-livecopilot \
  --run-type implementation \
  --summary-short "Rodada com facts enriquecidos." \
  --summary-full "Facts canonicos informados por arquivo JSON." \
  --checkpoint-path docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md \
  --facts-file docs/continuity/examples/sample_facts.json
```

## Facts minimos garantidos (fallback)
Mesmo sem facts explicitos, o builder garante:
1. `checkpoint` fact automatico
2. `pending` fact automatico (fallback conservador)

Se houver facts extras (`--facts-file` ou `--fact-inline`), eles sao adicionados.

## Fluxo semi-automatico
```bash
./scripts/run_continuity_capture.sh \
  --session-id agent-livecopilot \
  --actor codex \
  --run-type implementation \
  --summary-short "Integracao minima da continuidade ao fluxo operacional." \
  --summary-full "Payload canônico gerado por script e ingestão executada via wrapper." \
  --checkpoint-path docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md
```

## Hook opcional de encerramento (nova integracao)
Script:
- `scripts/run_round_closeout.sh`

Comportamento:
- **desabilitado** (default): nao altera o fluxo atual;
- **habilitado**: executa cadeia de continuidade completa:
  1. `run_continuity_capture.sh` (persistencia da rodada),
  2. `new_chat_context.sh --format json` (snapshot JSON),
  3. `new_chat_context.sh --format txt` (snapshot TXT + contexto final),
  4. manutencao de embeddings (opcional, somente faltantes) quando habilitada.
- em ambiente com PostgreSQL `peer` e execucao por root:
  - se nao houver DSN explicito no ambiente, aplica caminho direto seguro:
    1. build do payload como usuario atual,
    2. ingest via `runuser -u postgres`,
    3. segue para atualizacao de snapshot/contexto.
  - com DSN explicito, tenta `run_continuity_capture.sh`; se falhar, usa fallback seguro no mesmo formato.

Ativacao por flag:
```bash
./scripts/run_round_closeout.sh \
  --enable-continuity-hook \
  --project livecopilot \
  --session-id agent-livecopilot \
  --actor codex \
  --run-type implementation \
  --summary-short "Fechamento de rodada com hook de continuidade." \
  --summary-full "Persistencia, snapshot e contexto final gerados no encerramento." \
  --checkpoint-path docs/continuity/ROUND_SUMMARY_CONTINUITY_HOOK.md \
  --facts-file docs/continuity/examples/sample_facts.json
```

Ativacao por env var:
```bash
LIVECOPILOT_CONTINUITY_HOOK=1 ./scripts/run_round_closeout.sh ...mesmos argumentos...
```

Desativacao explicita:
```bash
./scripts/run_round_closeout.sh --disable-continuity-hook
```

Hook opcional de embedding maintenance no closeout:
- ativar por flag:
```bash
./scripts/run_round_closeout.sh \
  --enable-continuity-hook \
  --enable-embedding-maintenance \
  --embedding-maintenance-limit 200 \
  --embedding-maintenance-batch-size 10 \
  ...demais argumentos...
```
- ativar por env:
```bash
LIVECOPILOT_CONTINUITY_HOOK=1 \
LIVECOPILOT_CONTINUITY_EMBEDDING_MAINTENANCE=1 \
./scripts/run_round_closeout.sh ...demais argumentos...
```
- desativar explicitamente:
```bash
./scripts/run_round_closeout.sh --disable-embedding-maintenance
```

Artefatos atualizados quando habilitado:
- `docs/continuity/payloads/*.json`
- `docs/continuity/bootstrap/latest_snapshot.json`
- `docs/continuity/bootstrap/latest_snapshot.txt`
- `docs/continuity/opening_context/latest_new_chat_context.txt`

Observacao:
- no fallback `peer`, o payload continua auditavel em `docs/continuity/payloads/` e o `run_key` permanece idempotente.

## Integracao com fluxo real de rodada (ponte canonica)
Script:
- `scripts/run_real_round_flow.sh`

Ponto canonico escolhido:
- fechamento de rodada do `codex-supervisor` quando `state/last_action.json` e atualizado e o projeto alvo ja recebeu `STATUS.md` + `.supervisor/checkpoints/...`.

Motivacao da escolha:
- e o ponto unico e estavel em que a rodada ja terminou no fluxo operacional atual;
- evita parsing de markdown livre (usa JSON estruturado do supervisor);
- evita duplicar chamadas em varios comandos locais.

Comportamento:
- hook desligado: roda fluxo real e termina sem continuidade;
- hook ligado: apos o fim da rodada, chama `run_round_closeout.sh` com parametros derivados de `last_action.json`.
- embedding maintenance pode ser ligada junto no mesmo fluxo (tambem opcional).

Uso padrao do operador (rodada real completa):
```bash
./scripts/round \
  --enable-continuity-hook \
  --enable-embedding-maintenance \
  --facts-file docs/continuity/examples/sample_facts.json
```

Uso padrao do operador sem hook:
```bash
./scripts/round --disable-continuity-hook
```

Consulta operacional sem warning de `OPENAI_API_KEY`:
- usar `scripts/project_brain_query.sh` (wrapper com env canônico + execucao como `postgres`).
- evitar uso direto de `scripts/project_brain_query.py` no trilho operacional.

Uso equivalente direto no wrapper real (fallback manual preservado):
```bash
./scripts/run_real_round_flow.sh \
  --mode run-once \
  --enable-continuity-hook \
  --facts-file docs/continuity/examples/sample_facts.json
```

Uso em ambiente sem execucao de supervisor (replay estruturado do ultimo fechamento real):
```bash
./scripts/round \
  --from-last-action-only \
  --enable-continuity-hook \
  --facts-file docs/continuity/examples/sample_facts.json
```

Ativacao por env var (equivalente):
```bash
LIVECOPILOT_CONTINUITY_HOOK=1 \
LIVECOPILOT_CONTINUITY_EMBEDDING_MAINTENANCE=1 \
./scripts/round
```

Desativacao explicita:
```bash
./scripts/round --disable-continuity-hook
```

Opcional:
- `--dry-run`: gera payload e nao ingere.
- `--enable-embeddings` e `--embed-model`: repassados para `continuity_ingest.py`.
- `--enable-embedding-maintenance` / `--disable-embedding-maintenance`: controla manutencao de embeddings no closeout.
- `--embedding-maintenance-limit` / `--embedding-maintenance-batch-size` / `--embedding-maintenance-model`: parametros da manutencao incremental.

## Fluxo manual (fallback preservado)
Fallback 1 (wrapper real sem launcher):
```bash
./scripts/run_real_round_flow.sh --mode run-once --disable-continuity-hook
```

Fallback 2 (supervisor direto, sem ponte de closeout):
```bash
cd /lab/projects/codex-supervisor
python3 -m supervisor.main --target-project /lab/projects/livecopilot --run-once
```

Fallback 3 (captura e ingest totalmente manuais):
1. Gerar payload:
```bash
./.venv/bin/python scripts/continuity_build_payload.py \
  --session-id agent-livecopilot \
  --summary-short "..." \
  --summary-full "..." \
  --checkpoint-path docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md \
  --facts-file docs/continuity/examples/sample_facts.json
```
2. Ingerir payload:
```bash
./.venv/bin/python scripts/continuity_ingest.py --input docs/continuity/payloads/<payload>.json
```
3. Recall:
```bash
./.venv/bin/python scripts/continuity_recall.py --project livecopilot --runs 5 --facts 10 --json
```

## Validacao operacional
Checklist minimo:
1. payload JSON valido e salvo em `docs/continuity/payloads/`
2. ingest bem-sucedido a partir do payload gerado
3. novo registro em `project_runs`
4. fatos associados em `project_facts`
5. recall mostrando a rodada
6. reexecucao controlada sem duplicacao indevida

Smokes operacionais curtos (padrao da frente):
```bash
./scripts/smoke_round_continuity_default.sh
./scripts/smoke_project_brain_query_wrapper.sh
```

Os smokes validam:
- round padrao com continuidade + closeout + snapshot/contexto;
- persistencia em `project_runs`, `project_facts`, `project_memory_chunks`;
- `missing_embedding=0` para o run validado;
- consulta `semantic/hybrid` via wrapper com `semantic_warning=null`.

## Limitacoes atuais
- integracao ao fim da rodada e por invocacao explicita do wrapper (nao hook automatico global)
- facts automaticos ainda sao conservadores quando nao ha facts explicitos
- nao ha parse automatico robusto de `STATUS.md` para extrair fatos ricos
- embeddings seguem opcionais
