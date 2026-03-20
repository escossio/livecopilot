# POSTGRESQL Lexical Baseline Report

## Context
- Corpus: 4 chunks covering PostgreSQL architecture, SQL commands, indexing, and JSONB from postgresql.org.
- Stage: lexical validation right after chunking.

## Query Summary
| Query | Top chunk | Top1 relevance | Top3 quality | Notes |
| --- | --- | --- | --- | --- |
| postgresql architecture | `architecture-chunks.json` | Alta (descrição de shared buffers, WAL, replicação e config) | Alta (outros chunks mantêm foco técnico) | Sem ruídos; arquitetura central bem representada |
| sql commands postgres | `sql_commands-chunks.json` | Alta (lista de DDL/DML e transações) | Alta (usuários encontram SQL em todos os chunks, mas o top1 domina) | Cobertura direta dos comandos solicitados |
| postgres indexing | `indexing-chunks.json` | Alta (tipos de índice, GIN/GiST, partial, vacuum tuning) | Alta (top3 inclui SQL/architecture que apoiam) | Nenhuma lacuna observada |
| postgres jsonb | `jsonb-chunks.json` | Alta (operadores, indexing, performance) | Alta (outros chunks complementam com contexto) | Resposta limpa e pontual |

## Observações
- Nenhum chunk foi duplicado ou gerou ruído; cada top1 é específico e aparece no top3 com relevância similar.
- As quatro consultas-chave são respondidas diretamente pelos quatro chunks do corpus oficial.

## Decision
- **Status**: aprovado para `semantic_embeddings`
- Justificativa: cobertura completa das consultas definidas; não há lacunas bloqueantes nem ruído relevante.
