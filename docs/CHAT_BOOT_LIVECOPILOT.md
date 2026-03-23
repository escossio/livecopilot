# LIVE COPILOT — CHAT BOOT INSTRUCTION

Este arquivo serve como **instrução padrão de reinício de chat** para o projeto LiveCopilot.

Sempre que um novo chat for iniciado, copie e envie o conteúdo deste arquivo para restaurar o contexto operacional.

---

## MODELO_RECOMENDADO
mini

## JUSTIFICATIVA_DO_MODELO
Tarefa inicial focada em organização operacional e leitura de contexto.

---

## OBJETIVO
Restabelecer o contexto do projeto LiveCopilot e garantir:

- contrato de execução
- política de modelo
- watchdog operacional
- alinhamento de arquitetura

## FASE EM PREPARACAO

- `Etapa 17 - Correcao de estilo por sessao`
- escopo: ajuste de tom e formato por texto/voz na sessao corrente
- fora de escopo: memoria persistente global de estilo
- referencia: `docs/STAGE_17_1_STYLE_CORRECTION_SESSION_CONTRACT.md`

## FASE EM ABERTURA

- `Etapa 18 - Feedback Loop operacional`
- escopo: ler logs reais de uso, detectar padroes e gerar recomendacoes operacionais
- fora de escopo: alterar core de resposta nesta etapa inicial
- referencia: `scripts/usage_analysis.py`

## FASE EM PREPARACAO FUTURA

- `Etapa 19 - Guardrails de Evolucao`
- escopo: baseline protegida e checagem automatica de regressao por rodada
- fora de escopo: alterar core de resposta ou heuristicas
- referencia: `docs/LIVECOPILOT_GUARDRAIL_BASELINE.md`, `scripts/guardrail_check.py`

## REGRA OPERACIONAL DE QUALIDADE

Quando houver relatório de qualidade por rodada, a leitura operacional principal deve usar o delta da rodada atual.

- `histórico global` serve como telemetria acumulada
- `delta da rodada` serve como critério operacional para decisão de regressão ou correção

---

## NAO_FAZER

Não executar nesta etapa:

- ingestão de conhecimento
- alteração de ranking
- mudanças na API
- mudanças na UI

---

## ENTRADAS

Arquivos principais do projeto:

- AGENTS.md
- STATUS.md
- docs/

---

## FINALIDADE

Evitar perda de contexto quando:

- chat reinicia
- navegador trava
- nova sessão é criada
