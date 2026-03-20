# POSTGRESQL Semantic Baseline Report

## Context
- Índice: `data/semantic_index_experiments/postgresql/` (text-embedding-3-large, dim 3072, 4 embeddings).
- Bateria: arquitetura, SQL, indexação e JSONB.

## Query breakdown
| Query | Top1 chunk | Top3 quality | Ruído | Observações |
| --- | --- | --- | --- | --- |
| postgresql architecture | `architecture-chunks.json` | Alta | Nenhum | Aborda memória compartilhada, WAL e configurações de `postgresql.conf`. |
| sql commands postgres | `sql_commands-chunks.json` | Alta | Nenhum | Fornece DDL/DML e controle transacional coerente com o domínio. |
| postgres indexing | `indexing-chunks.json` | Alta | Nenhum | Cobre tipos de índice e tuning, sem mistura com outros domínios. |
| postgres jsonb | `jsonb-chunks.json` | Alta | Nenhum | Operadores, indexação e performance estão no topo. |

## Decisão
- Baseline aprovado; cada consulta retorna o chunk antecipado e o ranking semântico preserva a aderência total ao domínio PostgreSQL.
