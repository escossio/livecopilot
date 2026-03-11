# Continuity Bootstrap Context

## Objetivo
Gerar automaticamente um snapshot resumido do estado atual do projeto, usando somente a camada de continuidade (`project_runs` + `project_facts`), para iniciar novos chats com contexto consistente.

## Script
- `scripts/continuity_bootstrap_context.py`

## Entradas CLI
- `--project` (default: `livecopilot`)
- `--runs-limit` (default: `5`)
- `--facts-limit` (default: `10`)
- `--format` (`text|json`, default: `text`)
- `--output` (opcional, salva snapshot em arquivo)

## O que o snapshot traz
0. foco de execucao atual (`execution_focus`, derivado de `docs/project_status_state.json`)
1. ultimas rodadas (`recent_runs`)
2. decisoes ativas (`active_decisions`)
3. pendencias abertas (`pending_work`)
4. issues ativos (`active_issues`)
5. riscos ativos (`active_risks`)
6. fixes recentes (`recent_fixes`)
7. milestones recentes (`recent_milestones`)

## Regras
- fonte primaria: `project_runs` e `project_facts`
- respeita `fact_status`
- prioriza fatos mais recentes (`ORDER BY created_at DESC`)
- deduplicacao simples por `(fact_type, title_normalized)`
- nao depende de embeddings

## Uso
Formato texto (default):
```bash
./.venv/bin/python scripts/continuity_bootstrap_context.py --project livecopilot
```

Formato JSON:
```bash
./.venv/bin/python scripts/continuity_bootstrap_context.py \
  --project livecopilot \
  --runs-limit 8 \
  --facts-limit 20 \
  --format json
```

## Uso com arquivo (--output)
Convencao recomendada:
- diretorio: `docs/continuity/bootstrap/`
- arquivos reutilizaveis:
  - `latest_snapshot.txt`
  - `latest_snapshot.json`

Snapshot texto em arquivo:
```bash
./.venv/bin/python scripts/continuity_bootstrap_context.py \
  --project livecopilot \
  --output docs/continuity/bootstrap/latest_snapshot.txt
```

Snapshot JSON em arquivo:
```bash
./.venv/bin/python scripts/continuity_bootstrap_context.py \
  --project livecopilot \
  --format json \
  --output docs/continuity/bootstrap/latest_snapshot.json
```

Com `--output`, o script:
- cria diretorio pai automaticamente quando necessario;
- salva o snapshot no arquivo indicado;
- continua imprimindo o snapshot no stdout (compatibilidade retroativa);
- emite um aviso em `stderr` com o caminho salvo.

## Exemplo de saida (text)
```text
PROJECT CONTINUITY ACTION BRIEF
project: livecopilot

focus da rodada:
- ...

etapa atual:
- ...

ultimo progresso relevante:
- ...

bloqueio/trava atual:
- ...

proximo passo recomendado:
- ...

evitar agora:
- ...
```

## Observacao operacional
O script depende de `DATABASE_URL` explicita no ambiente (ou aliases `SEMANTIC_PG_DSN`/`LIVECOPILOT_DB_DSN`) e nao usa fallback para `peer` como caminho principal.
