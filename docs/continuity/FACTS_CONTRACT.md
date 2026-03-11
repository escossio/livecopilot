# Facts Contract (Continuity)

## Objetivo
Definir contrato explicito para facts canonicos no payload de continuidade, evitando parsing fragil de markdown livre.

## Por que facts explicitos
- eliminam ambiguidade na classificacao semantica da rodada;
- preservam auditabilidade (`source_path` e `source_section`);
- reduzem dependencia de heuristica sobre texto narrativo;
- melhoram qualidade do recall entre chats.

## Entrada recomendada
Principal:
- `--facts-file <arquivo.json>`

Opcional (casos simples):
- `--fact-inline "fact_type|fact_status|title|body|component|priority|source_path|source_section"`

Compatibilidade retroativa:
- `--facts-json` (alias legado de `--facts-file`)
- `--fact` (alias legado de `--fact-inline`)

## Estrutura JSON esperada
Arquivo deve conter uma lista de objetos:

```json
[
  {
    "fact_type": "decision",
    "title": "Separacao question_bank vs knowledge",
    "body": "Mantida separacao para evitar contaminacao da base documental por conteudo avaliativo.",
    "fact_status": "active",
    "component": "semantic-model",
    "priority": "high",
    "source_path": "STATUS.md",
    "source_section": "checkpoint 2026-03-09"
  }
]
```

## Campos obrigatorios por fact
- `fact_type`
- `fact_status`
- `title`
- `body`

## Campos opcionais por fact
- `component`
- `priority`
- `source_path`
- `source_section`

## Taxonomia valida
### fact_type
- `decision`
- `milestone`
- `issue`
- `fix`
- `pending`
- `insight`
- `risk`
- `checkpoint`
- `hypothesis`
- `abandoned_idea`

### fact_status
- `active`
- `historical`
- `partial`
- `abandoned`
- `superseded`

## Regras de fallback
Se nenhum fact explicito for fornecido:
1. builder gera 1 fact de `checkpoint` automaticamente;
2. builder gera 1 fact de `pending` automaticamente.

Isso preserva compatibilidade com o fluxo atual.

## Fluxo semi-automatico com facts explicitos
```bash
./scripts/run_continuity_capture.sh \
  --session-id agent-livecopilot \
  --run-type implementation \
  --summary-short "Rodada de continuidade com facts enriquecidos." \
  --summary-full "Facts canonicos explicitamente classificados via arquivo JSON." \
  --checkpoint-path docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md \
  --facts-file docs/continuity/examples/sample_facts.json
```

## Validacao aplicada
- validacao forte no builder para `fact_type`, `fact_status`, `title`, `body`;
- erro claro quando estrutura JSON for invalida ou campos obrigatorios estiverem ausentes.
