# Round Summary - Stage 11.3 Scope

## Subetapa alvo
- 11.3 - Acionamento externo complementar

## Objetivo da 11.3
Estruturar/operar o uso de fonte externa apenas como complemento controlado, condicionado ao gate de insuficiencia.

## O que ja estava implementado
- Gate local-first e politica de insuficiencia formalizados (11.1 concluida).
- Trilha auditavel de insuficiencia via knowledge gaps ativa (`project_brain_query` + `knowledge_gap_logger` + ingestao de gaps) (11.2 concluida).
- Invariantes contratuais explicitam busca externa complementar/controlada e vedam automacao cega.

## O que faltava para concluir 11.3
- Registrar de forma explicita e auditavel a decisao operacional de:
  - liberar acionamento externo complementar, ou
  - bloquear acionamento externo por contexto local suficiente.
- Padronizar essa decisao em artefato dedicado da etapa 11 (nao apenas em logs indiretos de gap).

## Criterio de conclusao da 11.3
"Integracoes externas usadas somente apos insuficiencia explicita, com trilha de decisao auditavel e sem romper invariantes/smokes."

## Avaliacao da lacuna
Lacuna restante e pequena: falta um utilitario operacional minimo para gate + trilha auditavel da decisao de acionamento externo.

## Decisao desta rodada
Implementar apenas o minimo necessario para fechar 11.3:
- utilitario de gate auditavel para decisao de acionamento externo complementar;
- registro em NDJSON da decisao;
- sem crawler/scraping e sem automacao de busca externa cega.

## Implementacao minima aplicada
- Novo utilitario: `scripts/external_search_decision.py`.
- Artefato auditavel: `data/external_search_decisions.ndjson`.
- Regra operacional implementada:
  - **allow_external_complement** apenas se existir insuficiencia explicita registrada em `data/knowledge_gaps.ndjson` para a mesma query (`empty_result`, `low_average_score`, `collapsed_diversity`);
  - caso contrario, **block_external_complement**.

## Validacao objetiva
- Cenario sem gap explicito: decisao `block_external_complement`.
- Cenario com gap explicito registrado (`collapsed_diversity`): decisao `allow_external_complement`.
- Evidencias registradas no NDJSON com `timestamp`, `query`, `decision` e bloco `evidence`.

## Conclusao da subetapa 11.3
Subetapa **11.3 concluida** no escopo atual: acionamento externo complementar agora possui gate explicito de insuficiencia e trilha de decisao auditavel.
