# Project Stage 11 Breakdown: Busca Externa Controlada

Data de consolidacao: 2026-03-11
Escopo: decomposicao oficial, curta e sequencial da Etapa 11 sem abrir frente paralela.

## Etapa mae
- Etapa 11: **Busca externa controlada**
- Status da etapa mae: **concluida**
- Dependencias oficiais: **3, 4, 6**

## Subetapas oficiais (sequencia de execucao)
| Subetapa | Nome curto | Descricao curta | Status | Dependencia | Criterio de conclusao |
|---|---|---|---|---|---|
| 11.1 | Gate local-first | Consolidar no fluxo a regra: consulta local primeiro e reconhecimento explicito de insuficiencia antes de camada externa. | concluida | 3, 4 | Regra local-first e politica de insuficiencia registradas no contrato e refletidas no fluxo oficial sem bypass. |
| 11.2 | Trilha auditavel de insuficiencia | Manter registro auditavel de lacunas (gap) quando contexto local for insuficiente, sem busca externa automatica cega. | concluida | 11.1, 5 | Fluxo `insuficiencia -> gap -> ingestao -> resolucao` ativo e documentado, com evidencias objetivas. |
| 11.3 | Acionamento externo complementar | Estruturar/operar o uso de fonte externa apenas como complemento controlado, condicionado ao gate de insuficiencia. | concluida | 11.1, 11.2 | Integracoes externas usadas somente apos insuficiencia explicita, com trilha de decisao auditavel e sem romper invariantes/smokes. |
| 11.4 | Curadoria para persistencia externa | Garantir que conhecimento vindo de fonte externa so persista apos avaliacao de relevancia/confianca/curadoria. | concluida | 6, 11.3 | Politica de curadoria aplicada de ponta a ponta para promocao persistente, sem ingestao externa automatica irrestrita. |
| 11.5 | Fechamento da etapa 11 | Encerrar etapa com validacao operacional e documental, mantendo escopo controlado e sem abrir expansao ampla (etapa 15). | concluida | 11.4 | Status da etapa 11 atualizado para concluida com handoff/round summary e evidencias comparaveis de operacao. |

## Ordem obrigatoria
11.1 -> 11.2 -> 11.3 -> 11.4 -> 11.5

## Foco interno atual
- Etapa 11 encerrada no escopo atual.
- Proxima etapa oficial aberta: 12 - Audio/compreensao plugavel (parcial).

## Limites de escopo desta etapa
- Nao inclui crawler/scraping autonomo.
- Nao inclui expansao ampla de busca externa (isso pertence a etapa 15).
- Nao altera missao core do produto (copiloto silencioso local-first).
