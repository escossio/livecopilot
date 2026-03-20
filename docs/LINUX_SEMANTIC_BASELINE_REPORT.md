# LINUX Semantic Baseline Report

## Context
- Índice: `data/semantic_index_experiments/linux/` (text-embedding-3-large, dim 3072, 4 embeddings).
- Perguntas sobre kernel, systemd, networking e `ps`.

## Query breakdown
| Query | Top1 chunk | Top3 quality | Ruído | Observações |
| --- | --- | --- | --- | --- |
| linux kernel subsystem | `kernel_subsystem-chunks.json` | Alta | Nenhum | Descreve subsistemas, sysfs, tuning e interfaces do kernel. |
| systemd overview | `systemd_overview-chunks.json` | Alta | Nenhum | Cobre units, journal e comandos `systemctl`. |
| linux networking basics | `networking-chunks.json` | Alta | Nenhum | Relata netfilter, namespaces e comandos `ip`/`ss`. |
| ps command linux | `man_ps-chunks.json` | Alta | Nenhum | Apresenta opções, estado de processos e uso real em automações. |

## Decisão
- Baseline aprovado; o ranking semântico retorna os chunks corretos sem introduzir ruído de outros domínios operacionais.
