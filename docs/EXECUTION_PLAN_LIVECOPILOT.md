# Plano de Execucao Operacional - Livecopilot

## Objetivo
Organizar as proximas etapas do projeto Livecopilot em ordem executavel, servindo como trilho formal das rodadas futuras do Codex.

## Estado Atual Resumido
- backend funcional
- laboratorio visual liveui funcional
- smoke E2E do chat funcional
- smoke de skill local funcional
- validacao estrutural da UI com data-testid
- pendencias reais ainda abertas

## Regras de Execucao
- executar em ordem, salvo replanejamento explicito
- nao abrir frentes paralelas sem registrar
- atualizar `STATUS.md` ao final de cada etapa executada
- gerar handoff quando a etapa justificar
- salvar evidencias reais de execucao
- marcar bloqueios e limitacoes explicitamente

## Etapas Organizadas

### 1. Corrigir erro funcional da pergunta sobre status do backend
- status inicial: pendente
- objetivo: remover o `500` observado em `/api/chat` quando perguntado sobre o status do backend
- escopo: investigar pipeline, roteamento, skill e conector envolvidos; corrigir o ponto minimo necessario
- criterios de sucesso: pergunta sobre status do backend retorna `200` e resposta coerente via UI/laboratorio visual
- dependencias: backend e liveui-lab ativos
- observacoes: erro `500` foi observado no smoke da skill local; validar pelo laboratorio visual

### 2. Consolidar controle operacional do laboratorio visual
- status inicial: pendente
- objetivo: garantir start/stop/restart previsiveis do liveui-lab
- escopo: revisar comportamento do `liveui-lab.target` no stop; ajustar relacionamento entre target e services
- criterios de sucesso: stop efetivo desliga services; start/restart liga services sem manual adicional
- dependencias: acesso a systemd e permissao operacional
- observacoes: registrar reboot como pendencia futura ou validacao controlada, se aplicavel

### 3. Consolidar validacoes funcionais locais estaveis
- status inicial: pendente
- objetivo: manter smoketests locais estaveis e reproduziveis
- escopo: manter smoke do chat e smoke de skill local sem regressao
- criterios de sucesso: execucoes repetidas com sucesso e evidencias salvas
- dependencias: liveui-lab operacional e backend funcional
- observacoes: ajustar apenas se houver fragilidade comprovada

### 4. Validacao semantica com base real e API realtime
- status inicial: pendente
- objetivo: validar o nucleo semantico com base real ingerida
- escopo: executar perguntas sobre conteudos ja ingeridos (foco inicial: Terraform e Kubernetes); validar coerencia com base local e pipeline real
- criterios de sucesso: respostas coerentes, rastreaveis e sem inconsistencias com a base
- dependencias: pipeline semantica local funcional e base ingerida acessivel
- observacoes: tratar como validacao funcional do nucleo semantico

### 5. Expansao controlada de testes funcionais
- status inicial: pendente
- objetivo: ampliar cobertura de testes do chat sem abrir voz ou conectores instaveis
- escopo: adicionar cenarios de uso util e cenarios de erro controlado, se fizer sentido
- criterios de sucesso: novos testes estaveis, sem flakiness e com evidencias
- dependencias: etapas 1-4 concluidas
- observacoes: manter expansao gradual

### 6. Retorno aos conectores sensiveis / validacoes avancadas
- status inicial: pendente
- objetivo: retomar conectores sensiveis com estabilidade comprovada
- escopo: revalidar conectores como MikroTik apenas apos consolidacao anterior
- criterios de sucesso: estabilidade, resposta e confiabilidade operacional comprovadas
- dependencias: etapas 1-5 concluidas
- observacoes: evitar regressao em runtime publicado

## Ordem Recomendada
- ordem: 1 -> 2 -> 3 -> 4 -> 5 -> 6
- dependencias: cada etapa depende da conclusao da etapa anterior, salvo replanejamento explicito

## Criterio de Avanco
- uma etapa pode ser considerada concluida quando os criterios de sucesso forem atingidos e houver evidencias registradas
- uma etapa deve ser pausada quando houver bloqueio tecnico, dependencia externa ou ambiguidade operacional nao resolvida

## Proxima Etapa Recomendada
- Etapa 1: corrigir erro funcional da pergunta sobre status do backend
