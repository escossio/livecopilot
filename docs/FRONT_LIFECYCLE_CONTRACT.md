# Contrato Global de Ciclo de Vida de Frentes

## 1) OBJETIVO
Estabelecer que nenhuma frente do projeto nasce, evolui ou se encerra sem contrato formal: abertura documentada, execução guiada e critérios de encerramento aprovados garantem clareza e rastreio de responsabilidades.

## 2) REGRA DE ABERTURA
Uma frente só passa para `opened` quando existir pelo menos:
- objetivo explicitado e alinhado ao roadmap vigente
- escopo delimitado com entregas e limites
- fora de escopo que define o que não será abordado
- artefatos esperados (formatos, destinos, responsáveis)
- ordem de execução prevista ou dependências claras
- critério de sucesso mensurável
- critério de encerramento que descreve o que será verificado para fechar a frente

## 3) REGRA DE EXECUÇÃO
A frente deve seguir o pipeline ou checklist associado, com checkpoints regimentados e handoffs registrados em `docs/`. Cada marco (freeze, parsing, chunking etc.) precisa de evidência documentada, e cada transição de estado deve registrar a última entrega e responsável.

## 4) REGRA DE FECHAMENTO
Só se chega ao estado `closed` quando todos os itens obrigatórios do checklist correspondente estiverem completos e validados pela equipe responsável. Não há fechamento provisório: o critério de encerramento acordado na abertura precisa ser satisfeito.

## 5) REGRA DE EXCEÇÃO
Quando a frente não puder ser fechada por dependências, falta de baseline ou bloqueios, ela deve ser marcada explicitamente como `blocked`, `closure_pending` ou `active` até que o impedimento seja resolvido. Esses estados devem incluir descrição curta do impedimento e quem monitora a resolução.

## 6) ESTADOS POSSÍVEIS DE UMA FRENTE
- `proposed` – ideia logada, aguardando contrato
- `opened` – contrato aprovado e execução autorizada
- `active` – trabalho em curso e checklist rodando
- `blocked` – impedimento externo ou falta de recurso
- `closure_pending` – checklist incompleto por dependência crítica
- `closed` – todos os itens finalizados e validado

## 7) POLÍTICA DE ABERTURA DE NOVA FRENTE
Por padrão, não abrimos nova frente enquanto a anterior não estiver em `closed`. Exceções devem ser justificadas, documentadas e aprovadas, detalhando por que a nova frente precisa coexistir com a anterior e quais mecanismos de isolamento ou prioridade serão adotados.

## 8) REGRA CRÍTICA PARA DOMÍNIOS DE INGESTÃO
Se o domínio exigir baseline semântica, o fechamento formal só ocorre após `semantic_baseline` e `embeddings` concluídos. Enquanto não houver embeddings válidos, o domínio permanece em `closure_pending` e não pode migrar para `closed`, mesmo que os demais itens estejam completos.

## 9) PRECHECK OBRIGATÓRIO DE FECHAMENTO
Antes de executar `closure_decision`, a frente deve passar por um `Front Closure Precheck` explícito e bloqueante. O precheck precisa validar documento da frente, final report, handoff final, semantic baseline, presença no `STATUS.md`, presença no índice de frentes, presença no registry de roteamento, `enabled_for_routing = true` e existência de embeddings compatíveis.

Se qualquer requisito obrigatório estiver ausente ou divergente, o fechamento é inválido e `closure_decision` não pode ser executado. Só seguir adiante com autorização explícita do operador após `PRECHECK PASSED`.
