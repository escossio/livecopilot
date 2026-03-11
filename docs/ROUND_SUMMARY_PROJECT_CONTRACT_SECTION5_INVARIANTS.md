# Round Summary - Section 5 Invariants (Project Contract)

## Objetivo da rodada
Consolidar a seção 5 do contrato com invariantes governantes do estado atual do Livecopilot, incluindo critérios claros de regressão arquitetural.

## Arquivo alterado
- `docs/PROJECT_CONTRACT.md`

## O que mudou
- Seção consolidada como `## 5. Invariantes do sistema`.
- Removida duplicidade entre "Invariantes do sistema" e "Invariantes de produto".
- Invariantes explícitos adicionados para:
  - saída principal visual/silenciosa em tela;
  - UI web local como core;
  - missão principal de apoio cognitivo realtime;
  - camada local como primeira consulta;
  - banco como cache semântico operacional com reconhecimento explícito de insuficiência;
  - busca externa complementar/controlada;
  - persistência externa com curadoria obrigatória;
  - caminho principal via `DATABASE_URL` com role de aplicação;
  - `postgres` restrito ao administrativo;
  - exclusão de `peer auth` e `runuser` do fluxo principal;
  - smokes como invariantes de sanidade;
  - mudanças pequenas/reversíveis com evidência comparável;
  - transcrição/compreensão como camada plugável com preferência operacional atual por API/modelo externo.
- Sub-seção nova: `Regressão arquitetural (sinal vermelho)` com casos objetivos para revisão futura.

## Escopo respeitado
- Sem alteração de código.
- Sem alteração de rotas, scripts, banco ou app.
- Ajuste restrito ao contrato e documentação de rodada.

## Resultado
A seção responde de forma auditável: "o que não pode quebrar sem que o Livecopilot deixe de ser o que ele é hoje".
