# LIVE COPILOT — PROJECT BRAIN

Este documento funciona como a **memória institucional do projeto**.

Registra:

- arquitetura
- decisões técnicas
- erros aprendidos
- direção do projeto

---

## VISÃO GERAL

LiveCopilot é um sistema de assistência técnica baseado em:

- base de conhecimento semântica
- recuperação de documentação
- síntese por LLM

Objetivo:

responder perguntas técnicas usando **documentação confiável**.

---

## PRINCÍPIOS

1. Knowledge First
2. Official Sources Priority
3. Minimal Hallucination
4. Operational Discipline

---

## ARQUITETURA

Componentes principais:

### Knowledge Ingestion
parsing, limpeza e chunking de documentação

### Semantic Search
recuperação vetorial e ranking

### Suggestion Layer
síntese final das respostas

---

## PROBLEMAS HISTÓRICOS

### Literatura editorial
livros geraram chunks pouco respondíveis.

### Front matter
metadata YAML dominava embeddings.

---

## ESTRATÉGIA ATUAL

OFFICIAL-FIRST KNOWLEDGE INGESTION

Priorizar documentação oficial e repositórios canônicos.

---

## PILOTO ATUAL

Domínio escolhido:

**Linguagem C**

Motivo:

- ainda não ingerido
- documentação clara

## PILOTOS CONCLUÍDOS

### Piloto C — encerramento 2026-03-17
- Status: concluído com sucesso; o domínio `c_programming` está isolado, validado e pronto para manutenção ou promoção controlada.
- Lição aprendida principal: validar o reforço semântico dos cabeçalhos oficiais (por exemplo `<assert.h>` e `read()`) garante que o ranking não apresente placeholders.
- Replicabilidade: o método official-first provado aqui (congelamento, chunking, embeddings isolados, utilitário local) pode ser aplicado a outros domínios, desde que o escopo e a bateria de perguntas sejam definidos previamente.
