# New Chat Context Utility

## Objetivo
Gerar um artefato textual pronto para copiar/colar ao iniciar novo chat, usando a camada de continuidade persistida.

## Script
- `scripts/new_chat_context.sh`

## O que faz
1. gera/atualiza snapshot atual via `continuity_bootstrap_context.py`;
2. salva snapshot bruto em arquivo;
3. monta arquivo final de contexto com cabecalho operacional;
4. informa os caminhos gerados no terminal.

## Entradas
- `--project` (default: `livecopilot`)
- `--output` (arquivo final do contexto)
- `--snapshot-output` (arquivo do snapshot bruto)
- `--format` (`txt` default, `json` opcional)

## Convencao padrao de saida
- snapshot bruto:
  - `docs/continuity/bootstrap/latest_snapshot.txt` (txt)
  - `docs/continuity/bootstrap/latest_snapshot.json` (json)
- contexto final:
  - `docs/continuity/opening_context/latest_new_chat_context.txt`

## Uso rapido
Padrao (txt):
```bash
./scripts/new_chat_context.sh --project livecopilot
```

## Integracao no encerramento de rodada
Quando usado com `scripts/run_round_closeout.sh` e hook habilitado, o `new_chat_context.sh` e chamado automaticamente para:
- atualizar `latest_snapshot.json`,
- atualizar `latest_snapshot.txt`,
- gerar `latest_new_chat_context.txt`.

Isso evita chamada manual da cadeia ao fim de cada rodada relevante.
O script usa credencial canonica via `DATABASE_URL` a partir de `/etc/livecopilot-semantic.env` (sem fallback de `peer`/`runuser` no fluxo normal).

No fluxo real com supervisor, o comando padrao do operador e:
```bash
./scripts/round
```

`scripts/round` delega para `scripts/run_real_round_flow.sh` e mantem o fluxo de closeout opcional por hook, sem parsing de markdown livre.

Exemplo com hook habilitado:
```bash
LIVECOPILOT_CONTINUITY_HOOK=1 ./scripts/round
```

Replay estruturado do ultimo fechamento real:
```bash
./scripts/round --from-last-action-only --enable-continuity-hook
```

Fallback manual preservado:
```bash
./scripts/run_real_round_flow.sh --mode run-once --disable-continuity-hook
```

Com caminhos explicitos:
```bash
./scripts/new_chat_context.sh \
  --project livecopilot \
  --snapshot-output docs/continuity/bootstrap/latest_snapshot.txt \
  --output docs/continuity/opening_context/latest_new_chat_context.txt
```

Snapshot JSON + contexto final:
```bash
./scripts/new_chat_context.sh \
  --project livecopilot \
  --format json \
  --snapshot-output docs/continuity/bootstrap/latest_snapshot.json \
  --output docs/continuity/opening_context/latest_new_chat_context.txt
```

## Snapshot bruto vs contexto final
- snapshot bruto: saida direta do bootstrap (`txt` acionavel ou `json` estruturado).
- contexto final: sempre texto operacional curto para abrir novo chat com foco de execucao.
  - inclui: foco da rodada, etapa atual, ultimo progresso, bloqueio, proximo passo, evitar agora e riscos de deriva.

## Observacao operacional
Quando `--format json` e usado:
- `latest_snapshot.json` preserva dump estruturado completo para auditoria;
- `latest_new_chat_context.txt` continua compacto/acionavel (gera bloco em texto automaticamente).
