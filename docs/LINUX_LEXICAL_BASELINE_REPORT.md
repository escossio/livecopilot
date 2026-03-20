# LINUX Lexical Baseline Report

## Context
- Corpus: 4 chunks (kernel subsystems, systemd overview, networking, ps man page) extracted de kernel.org, freedesktop.org e man7.org.
- Stage: lexical baseline antes de qualquer etapa semântica.

## Query Summary
| Query | Top chunk | Top1 relevance | Top3 quality | Notes |
| --- | --- | --- | --- | --- |
| linux kernel subsystem | `kernel_subsystem-chunks.json` | Alta (scheduling, memory, sysfs, tuning knobs) | Alta (outros chunks são systemd/networking mas mantêm foco técnico) | Sem ruído; direcionado ao kernel upstream |
| systemd overview | `systemd_overview-chunks.json` | Alta (unidades, journal, controle) | Alta (top3 inclui kernel e networking mas relevantes para administração) | Cobertura direta dos diretórios desejados |
| linux networking basics | `networking-chunks.json` | Alta (network namespaces, netfilter, `ip`, `ss`) | Alta (os demais chunks mantêm foco operacional) | Nenhuma lacuna; top1 confere com a query |
| ps command linux | `man_ps-chunks.json` | Alta (opções, uso com systemd, TTY/STAT) | Alta (top3 com kernel/systemd complementa o contexto) | Texto de manual puro, sem ruído de marketing |

## Observações
- O corpus responde as perguntas-chave do domínio de administração Linux sem ambiguidades.
- Chunking manteve um trecho representativo por documento e preservou o texto técnico intacto.

## Decision
- **Status**: aprovado para `semantic_embeddings`
- Justificativa: todos os tópicos obrigatórios possuem top1 relevante e o top3 permanece útil; nenhuma lacuna identificada.
