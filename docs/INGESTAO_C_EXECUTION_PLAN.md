# INGESTAO C — EXECUTION PLAN

Este documento define o plano enumerado da nova frente de ingestão official-first para linguagem C.

---

## CONTEXTO

A ingestão antiga misturou literatura editorial extensa com documentação oficial.
A nova estratégia passa a priorizar fontes oficiais e corpus mais respondível.

Domínio piloto escolhido:

**Linguagem C**

---

## DIRETRIZ

Estratégia:

**OFFICIAL-FIRST KNOWLEDGE INGESTION**

O corpus legado permanece preservado, mas fora da prioridade principal de busca.

---

## ETAPAS

1. definir fontes oficiais de C
2. definir critérios de confiança
3. clonar e congelar fontes
4. parsing e limpeza de metadata
5. chunking
6. ingestão local
7. persistência vetorial
8. subset de validação
9. baseline curta
10. baseline ampliada
11. critérios de sucesso
12. decisão de adoção

---

## CRITÉRIOS DE SUCESSO

- chunks limpos e respondíveis
- ausência de front matter no topo
- subset inicial com respostas coerentes
- baseline curta estável
- baseline ampliada útil para regressão

---

## OBSERVAÇÃO

Este plano deve ser seguido por etapas, sem misturar novas frentes antes da validação do piloto em C.
