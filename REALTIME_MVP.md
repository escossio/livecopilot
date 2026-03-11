# Realtime Copilot MVP (Modulo 1)

## A) Objetivo do modulo Realtime Copilot
Entregar sugestoes curtas e uteis em tempo quase real a partir de contexto recente da conversa, usando a base semantica existente do projeto.

Objetivo operacional do MVP:
- ouvir/receber contexto em tempo real (inicialmente texto)
- consultar base semantica existente (sem alterar o Knowledge Core)
- sugerir resposta curta e util com baixa latencia

## B) Casos de uso prioritarios
1. entrevista tecnica (resposta rapida com framing tecnico)
2. conversa com recrutador/RH tecnico (clareza curta + termos de mercado)
3. reuniao tecnica curta (resumo + proximo passo)
4. consulta rapida contextual (pergunta tecnica direta)

## C) Entradas do modulo
Entradas minimas do contrato MVP:
- `transcript_text`: texto incremental (ou texto manual)
- `is_question`: flag simples de pergunta detectada (`?` + heuristica)
- `recent_context`: janela curta de turnos (default atual: `MAX_CONTEXT_TURNS=8`)
- `mode`: `interview | study | ops | generic` (default: `generic`)

Payload minimo recomendado (nivel API interna):
```json
{
  "transcript_text": "como explicar diferença entre readiness e liveness probe?",
  "is_question": true,
  "recent_context": [
    {"speaker": "user", "text": "estou em entrevista de kubernetes"}
  ],
  "mode": "interview"
}
```

## D) Saidas do modulo
Saidas minimas do contrato MVP:
- `short_answer`: resposta curta sugerida (1 frase util)
- `support_bullets`: 2-4 bullets de apoio
- `confidence_or_origin`: sinal simples de confianca/origem (ex.: `semantic_api`, `local_knowledge_search`, `fallback`)
- `references_context` (opcional): resumo curto de contexto/fontes

Payload minimo recomendado de saida:
```json
{
  "short_answer": "Readiness indica se o pod pode receber trafego; liveness detecta se ele travou e precisa reinicio.",
  "support_bullets": [
    "Readiness falha remove endpoint do Service",
    "Liveness falha reinicia container",
    "Evite usar o mesmo endpoint para as duas probes"
  ],
  "confidence_or_origin": "semantic_api",
  "references_context": "kubernetes probes + exemplos operacionais"
}
```

## E) Pipeline logico minimo
Pipeline MVP (sem pilha pesada):
1. captura/transcricao
- fluxo inicial: entrada textual manual + `transcribe_mock()`
2. buffer de contexto curto
- `ConversationState.transcript` com janela curta
3. deteccao de intencao/pergunta
- classificacao simples ja existente (`_classify_input`)
4. consulta ao Knowledge Core
- tentativa primaria: `/semantic/search`
- fallback local: `search_knowledge_chunks_with_debug()`
5. compressao da resposta
- sintetizar para resposta curta + bullets (via `suggestions.py`)
6. renderizacao rapida
- snapshot em `/ingest` + broadcast websocket (quando habilitado)

## F) Requisitos de latencia (MVP)
Contrato pratico de latencia para esta fase:
- resposta parcial: ate ~2s apos entrada textual (quando sem dependencia externa critica)
- resposta curta final: alvo de 2-5s na maioria dos casos
- fallback local deve evitar silencio longo quando semantic API falhar

Nao entra benchmark pesado nesta fase; o foco e usabilidade de conversa ao vivo.

## G) Modos de fallback
1. sem transcricao
- fallback para entrada manual de texto (ja suportado por `/ingest`)
2. sem contexto suficiente
- resposta curta neutra + pergunta de clarificacao
3. sem resultado forte na busca
- resposta conservadora com orientacao geral + sugestao de proximo passo
4. indisponibilidade semantic API
- fallback automatico para `local_knowledge_search`

## H) Dependencias com modulos existentes
Dependencias diretas:
- Knowledge Core (Modulo 2)
  - `semantic_min_api` (`/semantic/search`)
  - `knowledge_search` local (fallback)
  - `build_context_from_results` para contexto resumido
- Question Bank / Gap Learning (Modulo 3)
  - uso consultivo em fase posterior para reforcar lacunas e trilhas
  - nao bloqueia fluxo basico realtime

Dependencia explicita que NAO e necessaria para o MVP realtime:
- Ops / Runbook Mode (Modulo 5)
  - runbooks/incidentes/comandos/metricas nao sao pre-requisito do modulo realtime

## I) MVP estrito
Entra no MVP agora:
- fluxo texto/manual ponta a ponta
- contexto curto em memoria
- deteccao simples de pergunta/intencao
- consulta semantica com fallback local
- resposta curta + apoio + origem resumida

Nao entra no MVP agora:
- automacao avancada
- UI complexa
- voz bidirecional sofisticada
- execucoes automaticas
- integracao pesada com runbooks/incidentes
- refatoracao ampla de pipeline semantico

## J) Roadmap do modulo Realtime
### Fase 1: texto/manual
- consolidar contrato de entrada/saida realtime via texto
- estabilizar latencia percebida com fallback robusto

### Fase 2: transcricao incremental
- evoluir de `transcribe_mock` para fonte incremental (sem trocar arquitetura do nucleo)
- manter compatibilidade com entrada manual

### Fase 3: contexto continuo
- melhorar janela contextual e sinais de continuidade entre turnos
- reduzir ruido em trocas de topico durante conversa ao vivo

### Fase 4: refinamentos de UX
- melhorar apresentacao de resposta curta/bullets/origem
- calibrar experiencia para entrevista e reuniao curta sem aumentar complexidade de infraestrutura

## Interfaces minimas entre Realtime Copilot e Knowledge Core
Contrato recomendado de consulta (MVP):
- request:
```json
{
  "query": "texto atual",
  "limit": 3,
  "return_context": true
}
```
- response minima esperada:
```json
{
  "status": "ok",
  "count": 3,
  "results": [],
  "context": "resumo curto"
}
```
- comportamento de erro:
  - falha semantic API -> fallback automatico local
  - falha local tambem -> resposta conservadora e orientacao de clarificacao
