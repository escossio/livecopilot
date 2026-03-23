# Livecopilot Guardrail Baseline

Baseline protegida para a Etapa 19. Esta referência serve para bloquear regressões nas rodadas futuras.

## Prompts protegidos

1. Sobre python
2. No Linux?
3. o que é docker?
4. como rodar um container nginx?
5. docker -> kubernetes -> deploy
6. responde mais humano
7. responde mais direto
8. faz em passo a passo
9. usa hipótese + teste

## Comportamento esperado

- respostas específicas, naturais e úteis
- sem `FALLBACK_DISFARCADO`
- sem `DRIFT_DE_DOMINIO`
- sem `IDIOMA_ERRADO`
- `style_correction` explícito continua sendo respeitado na sessão
- multi-turn legítimo continua funcionando

## Labels aceitáveis

- `OK`
- `style_correction` apenas como evento de logging/controle, não como label de resposta final

## Critérios mínimos de aceitação

- todos os prompts protegidos devem ficar `OK`
- nenhum prompt protegido pode cair em fallback disfarçado
- nenhum prompt protegido pode cair em drift
- nenhum prompt protegido pode sair em idioma errado
- `round_health_score` mínimo: `1.0` para a baseline protegida
- o guardrail deve retornar `PASS` somente quando todos os prompts protegidos passarem

## Observação operacional

Esta baseline não altera o core de resposta. Ela apenas define o piso de estabilidade para checagens futuras.
