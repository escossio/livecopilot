# Stage 14.1 ASR Local Contract (Operacional)

Data: 2026-03-11
Status: ativo (contrato definido)

## 1) Finalidade
Definir o contrato operacional minimo do **ASR local robusto** antes de implementacao funcional, preservando o produto como copiloto silencioso realtime.

## 2) O que significa "ASR local robusto" neste projeto
ASR local robusto e a capacidade de transcrever entrada de audio para texto em fluxo realtime com:
- latencia previsivel para uso conversacional;
- comportamento estavel em indisponibilidade parcial;
- degradacao controlada para `external` ou `mock` sem quebrar o fluxo;
- telemetria minima para auditoria operacional.

Nao significa, nesta subetapa:
- trocar missao principal para produto falado;
- exigir hardware novo como pre-condicao;
- remover fallback externo/mock.

## 3) Objetivos operacionais (14.1)
1. Formalizar matriz de runtime de transcricao: `local | external | mock`.
2. Definir requisitos minimos de latencia e robustez para considerar o modo local "apto".
3. Definir politica explicita de fallback e degradacao.
4. Definir criterios objetivos de validacao para futuras subetapas (14.2+).
5. Registrar limites de hardware do ambiente atual para evitar premissas invalidas.

## 4) Requisitos minimos de latencia (alvos contratuais)
Para fluxo realtime conversacional, o contrato de 14.1 adota:
- transcricao parcial (chunk curto): alvo `<= 2.0s` p95;
- consolidacao de trecho final: alvo `<= 5.0s` p95;
- degradacao/fallback acionado: resposta em `<= 1.0s` para nao gerar silencio prolongado.

Observacao:
- Esses alvos sao criterios de aceite operacional das proximas subetapas.
- Nesta 14.1 nao ha benchmark nem implementacao.

## 5) Requisitos minimos de robustez
Para considerar o ASR local robusto em uso controlado:
1. Sem erro fatal no fluxo `/ingest`/`/realtime/respond` quando ASR local falhar.
2. Fallback automatico e auditavel para `external` ou `mock`.
3. Preservacao de metadados de trilha (`configured_provider`, `effective_provider`, `fallback_used`).
4. Sem perda de comportamento padrao silencioso da UI.
5. Sem dependencia de voz de saida para completar resposta textual.

## 6) Limites de hardware suportados (contrato inicial)
- O contrato **nao assume hardware novo**.
- Baseline atual: ambiente com limitacoes reais, historicamente operando com preferencia por provider externo para transcricao.
- Regra: enquanto nao houver evidencia objetiva de capacidade local sustentada, `local` permanece opcional e nunca obrigatorio.
- Qualquer requisito de CPU/GPU/RAM/dispositivo de captura que exceda o baseline atual deve ser explicitado como premissa antes de implementacao.

## 7) Politica de fallback (runtime matrix)
Precedencia contratual por configuracao:
1. `provider=local`
   - tenta local;
   - se falhar ou indisponivel, fallback para `external` quando disponivel;
   - sem `external`, fallback para `mock`.
2. `provider=external`
   - tenta externo;
   - se indisponivel/falhar, fallback para `mock`.
3. `provider=mock`
   - usa mock diretamente.
4. `provider` invalido
   - registrar evento de provider indisponivel;
   - fallback para `mock`.

Invariantes de fallback:
- nunca quebrar o fluxo principal;
- nunca bloquear snapshot/resposta textual;
- sempre registrar trilha de provider efetivo e uso de fallback.

## 8) Cenarios de degradacao aceitavel
1. Captura live indisponivel:
   - degradar para caminho textual/manual sem erro fatal.
2. ASR local indisponivel/instavel:
   - degradar para `external` (quando houver credencial) ou `mock`.
3. External indisponivel (sem credencial/rede/erro de API):
   - degradar para `mock`.
4. Falha total de transcricao:
   - manter resposta conservadora com pedido de clarificacao, sem interromper UI.

## 9) Criterios de validacao (para 14.2+)
Checklist minimo de aceite operacional futuro:
1. `GET /status` expor provider configurado e disponibilidade efetiva de caminho local/externo.
2. Casos de teste cobrindo `local`, `external`, `mock` e provider invalido.
3. Evidencia de fallback sem quebra de fluxo (`status=ok` em `/ingest` e `/realtime/respond`).
4. Evidencia de latencia dentro dos alvos definidos no item 4 em rodada de validacao.
5. Evidencia de metadados de trilha de transcricao por turno/snapshot.

## 10) Guardrails obrigatorios da Etapa 14
1. Nenhuma mudanca funcional nesta subetapa 14.1.
2. Nao abrir frente paralela fora da Etapa 14.
3. Nao alterar o contrato de missao principal (copiloto silencioso).
4. Nao transformar fallback em erro fatal.
5. Nao assumir hardware inexistente sem registro explicito.

## 11) Fora de escopo da 14.1
- Implementar provider local robusto.
- Alterar `audio_capture.py`, `transcription.py`, `context.py`.
- Alterar rotas/API/fluxo funcional.
- Benchmark de performance em producao.
