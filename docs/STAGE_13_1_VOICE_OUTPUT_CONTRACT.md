# Stage 13.1 Voice Output Contract (Opt-in)

Data: 2026-03-11
Status: ativo (contrato definido)

## 1) Finalidade
Estabelecer contrato minimo para saida falada realtime como capacidade opcional, sem alterar o comportamento padrao silencioso do produto.

## 2) Regra principal
- `voice_output` e **opt-in**.
- Comportamento padrao do Livecopilot permanece **silencioso** (UI textual/sugestoes).

## 3) Flags minimas
- `VOICE_OUTPUT_ENABLED`:
  - tipo: boolean
  - default: `false`
  - efeito: habilita/desabilita tentativa de saida falada.
- `VOICE_OUTPUT_PROVIDER`:
  - tipo: string
  - default: `external`
  - valores esperados nesta etapa: `external`, `none`.
- `VOICE_OUTPUT_MODEL`:
  - tipo: string
  - default: provider-defined
  - efeito: selecionar modelo de voz quando provider externo estiver ativo.

## 4) Contrato minimo de request/response (quando aplicavel)
Request minimo (nivel logico):
```json
{
  "text": "resposta curta para vocalizacao",
  "mode": "interview",
  "voice_output_enabled": true
}
```

Response minima esperada:
```json
{
  "voice_status": "disabled|ready|fallback_silent|error",
  "voice_provider": "external|none",
  "voice_enabled_effective": false
}
```

## 5) Semantica operacional
- `disabled`: voz desativada por flag/config; fluxo silencioso segue normal.
- `ready`: provider apto e resposta falada disponivel (quando implementado nas subetapas seguintes).
- `fallback_silent`: tentativa de voz nao disponivel; sistema segue em modo silencioso sem erro fatal.
- `error`: falha nao bloqueante de voz com degradacao para modo silencioso.

## 6) Guardrails obrigatorios
1. Voz nao pode virar comportamento padrao.
2. UI silenciosa continua como saida primaria.
3. Falha/ausencia de voz nao bloqueia `/ingest` e `/realtime/respond`.
4. Sem dependencia de hardware local pesado.
5. Sem abrir frente de ASR local (Etapa 14 continua separada).
6. Provider externo plugavel e o caminho preferencial inicial desta etapa.

## 7) Fora de escopo da 13.1
- Implementacao funcional de TTS.
- Streaming de audio de saida em producao.
- Mudancas de arquitetura amplas.
- Alteracao de missao principal do produto.

## 8) Critério de aceite da 13.1
- Contrato 13.1 documentado (este arquivo).
- Escopo da subetapa documentado (`ROUND_SUMMARY_STAGE_13_1_SCOPE`).
- Estado oficial refletindo 13.1 concluida e proximo foco 13.2.
