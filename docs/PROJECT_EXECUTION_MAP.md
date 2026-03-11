# Project Execution Map: Livecopilot

## 1. Objetivo do mapa de execução
Este mapa existe para orientar execução e priorização em sessões longas, separando claramente:
- o que já foi concluído;
- o que está parcial/em observação;
- o que ainda não começou;
- o que está fora do escopo atual.

Documento complementar (não substitui):
- `docs/PROJECT_CONTRACT.md` (governança/missão)
- `STATUS.md` (diário detalhado de checkpoints)

## 2. Visão macro do projeto por fases
Fase A - Fundação e reancoragem do produto
- MVP local, UI web, fluxo de ingestão textual, contexto e sugestões.
- Reancoragem formal do propósito em copiloto silencioso realtime.

Fase B - Núcleo de conhecimento em camadas
- Knowledge base + question bank separados.
- Gap logic, coverage/action plan e curadoria operacional.

Fase C - Continuidade e memória operacional
- `project_runs`/`project_facts`/`project_memory_chunks` integrados ao fluxo de rodada.
- `scripts/round` como trilho operacional padrão.

Fase D - Project Brain (apoio)
- Query structured/semantic/hybrid com wrapper oficial.
- Bateria offline de avaliação + calibração controlada de ranking.

Fase E - Estabilização pós-calibração (atual)
- Observação operacional contínua.
- Decisão de recalibração somente quando houver regressão material.

## 3. Etapas concluídas
- Contrato governante criado e refinado (`docs/PROJECT_CONTRACT.md`).
- Core de produto silencioso em tela consolidado (UI local + snapshot + websocket).
- Pipeline de conhecimento separado e funcional:
  - `knowledge` (referência/explicação)
  - `question_bank` (lacuna/cenário/pergunta)
- Continuidade operacional consolidada com closeout, snapshot e contexto de abertura.
- Wrapper oficial de Project Brain (`scripts/project_brain_query.sh`) consolidado.
- Bateria oficial de avaliação offline de ranking consolidada.
- Calibração controlada formalmente encerrada (`max_share semantic=0.25` mantido).

## 4. Etapas parcialmente concluídas
- Camada de captura/compreensão de áudio:
  - plugável e com caminho operacional atual baseado em API/modelo externo,
  - ainda coexistindo com trilha local simplificada/mock.
- Busca externa controlada:
  - política definida no contrato,
  - implementação ainda parcial e concentrada nas integrações existentes.
- Estabilidade de ranking pós-calibração:
  - operação funcional (smokes verdes),
  - com sinal recente de regressão material de diversidade em observação contratual.

## 5. Etapas ainda não iniciadas
- Resposta falada em tempo real como capacidade central de produto.
- Pilha robusta de transcrição local em hardware dedicado para realtime contínuo.
- Expansão formal da busca externa online além das integrações atuais controladas.
- Frente dedicada de infraestrutura DB para reduzir dependência de `runuser`/`peer auth` no operacional local.

## 6. Frentes encerradas formalmente
- Encerramento da frente de continuidade no escopo atual (com smokes e trilho padrão ativos).
- Encerramento da calibração controlada de ranking (decisão mantida: `max_share semantic=0.25`).
- Encerramento da criação/refino do contrato governante do projeto.

## 7. Dependências entre etapas/frentes
- Missão de produto (contrato) -> define o que pode ou não ser priorizado.
- Realtime/UI core -> depende de contexto + recuperação de conhecimento.
- Recuperação de conhecimento -> depende de ingestão/curadoria e separação `knowledge` vs `question_bank`.
- Continuidade -> depende de closeout operacional estável (`scripts/round`).
- Project Brain (apoio) -> depende de continuidade/memória + bateria de avaliação.
- Calibração de ranking -> depende de evidência offline comparável + smokes operacionais.

## 8. Sequência recomendada de execução a partir do estado atual
1. Tratar a estabilidade de ranking pós-calibração como gate de curto prazo (diagnóstico já existente aponta regressão de diversidade).
2. Se reabrir calibração, manter escopo mínimo e controlado:
   - sem schema;
   - com before/after na bateria oficial;
   - sem mudanças em cascata.
3. Fechar nova observação curta (1-2 ciclos) após eventual ajuste para confirmar estabilidade.
4. Só depois retomar frente de bootstrap/contexto inicial e outras evoluções secundárias.
5. Manter operação diária com smokes invariantes antes de cada avanço de frente.

## 9. Riscos de deriva/priorização incorreta
- Promover modo satélite (Project Brain/Ops) como missão principal e desancorar o core silencioso realtime.
- Reabrir tuning contínuo sem evidência comparável (ansiedade de calibração).
- Misturar frentes encerradas com backlog futuro e perder foco operacional.
- Tratar base local como conhecimento completo e ignorar política de insuficiência/curadoria.
- Executar mudanças funcionais antes de resolver sinais objetivos de regressão de qualidade.

## 10. Critério de uso do mapa em novas rodadas
A cada nova rodada:
1. Confirmar em qual bloco a tarefa cai: concluído, parcial, observação, não iniciado ou fora de escopo.
2. Validar dependências explícitas antes de executar.
3. Priorizar pela sequência recomendada atual.
4. Revalidar alinhamento com o contrato pela pergunta:
   - "isso aproxima ou afasta o Livecopilot da missão principal de copiloto silencioso de conversação técnica em tempo real?"
5. Registrar checkpoint curto no `STATUS.md` ao concluir a etapa.

## O que depende de quê
- Contrato governante -> todas as priorizações.
- Núcleo realtime silencioso -> contexto + busca local + fallback controlado.
- Busca/ranking -> ingestão e curadoria de `knowledge`/`question_bank`.
- Continuidade/Project Brain -> saúde da operação de rodada (`scripts/round` + smokes).
- Evoluções futuras (voz/local ASR robusto) -> estabilidade do core atual + capacidade operacional sustentada.

## Sequência recomendada atual
- Primeiro: resolver/confirmar estabilidade pós-calibração de ranking (frente em observação).
- Segundo: manter trilho operacional e smokes verdes como invariantes.
- Terceiro: avançar para frentes de contexto inicial/bootstrap somente após estabilidade confirmada.
- Quarto: tratar futuras expansões (voz/local ASR robusto/external search ampliado) como backlog fora do escopo imediato.
