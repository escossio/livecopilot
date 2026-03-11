# Project Origin: Livecopilot

## Por que o projeto surgiu
O projeto nasceu para resolver um problema prático de conversas técnicas em tempo real: responder com baixa latência, com clareza, e com base em contexto técnico verificável (não só respostas genéricas).

No início, o foco foi um MVP local executável (FastAPI + UI simples + modo mock) para validar fluxo ponta a ponta antes de integrar captura/transcrição real.

## Problema que tenta resolver
Transformar entrada conversacional (inicialmente texto, depois realtime) em resposta curta e útil, com:
- contexto recente da conversa,
- apoio de base técnica,
- noção explícita de lacunas de conhecimento,
- caminho prático para expansão da base.

## Ideia central desde o início
A ideia evoluiu de "assistente de resposta" para "motor de aprendizagem guiada por lacunas":
- questionários/perguntas revelam o que falta,
- documentação preenche o que falta,
- o sistema mede cobertura e prioriza ingestão.

## Princípios-guia no desenho do sistema
Princípio 1: **"saber o que não sabe"**
- aparece no `question_bank` separado,
- no comparador `question_bank vs knowledge`,
- em `covered/partial/missing` e no plano de ação.

Princípio 2: **"não uma base estática, mas uma máquina que aprende pela revelação da própria ignorância"**
- aparece na `gap queue`,
- na priorização por recorrência/gravidade,
- na consolidação temática em blocos acionáveis,
- no ciclo contínuo: pergunta -> lacuna -> ingestão orientada.

## Fonte e confiança
- Fonte primária: `chat_livecopilot.txt`.
- Fonte secundária de apoio: `ARCHITECTURE.md`, `REALTIME_MVP.md`, `STATUS.md`.
- Onde houver fase sem data exata, a narrativa usa ordem evolutiva (fase inicial, intermediária, posterior).
