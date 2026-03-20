# Handoff Livecopilot Response Guidance Maintenance 20260314T023355Z

## Objetivo
Criar um fluxo controlado para adicionar, revisar, ativar e desativar regras de `response_guidance`, mantendo `data/response_guidance.json` como fonte canonica e sem abrir aprendizado automatico.

## Mecanismo criado
- CLI interno:
  - `python -m app.services.response_guidance`

## Fonte canonica
- `data/response_guidance.json`

## O que o CLI faz
- lista regras
- mostra regra por id
- adiciona regra nova validando estrutura
- atualiza resposta/regra existente
- desativa regra via `active=false`
- reativa regra existente

## Comandos principais
- listar regras:
```bash
./.venv/bin/python -m app.services.response_guidance list
```

- mostrar regra:
```bash
./.venv/bin/python -m app.services.response_guidance show --id fallback_unmapped_target
```

- adicionar regra:
```bash
./.venv/bin/python -m app.services.response_guidance add \
  --id greeting_e_ai \
  --scope livecopilot_reply \
  --trigger-type normalized_text \
  --match-examples '["e ai"]' \
  --answer 'E ai. Pode mandar a pergunta.' \
  --bullets '["Se quiser, eu respondo em texto curto."]'
```

- atualizar resposta:
```bash
./.venv/bin/python -m app.services.response_guidance update \
  --id fallback_unmapped_target \
  --answer 'Ainda nao tenho esse alvo mapeado com confianca.'
```

- desativar:
```bash
./.venv/bin/python -m app.services.response_guidance disable --id greeting_e_ai
```

- reativar:
```bash
./.venv/bin/python -m app.services.response_guidance enable --id greeting_e_ai
```

## Garantias implementadas
- `version` preservado
- validacao estrutural antes de salvar
- ids duplicados sao rejeitados
- `updated_at` e atualizado corretamente
- escrita atomica com arquivo temporario
- regra nao e apagada por padrao

## Testes adicionados
- carregar arquivo atual
- adicionar regra valida
- rejeitar regra invalida
- impedir id duplicado
- desativar regra
- reativar regra
- atualizar `preferred_response` mantendo integridade do arquivo
- exercitar fluxo principal do CLI

## Arquivos alterados
- `app/services/response_guidance.py`
- `tests/test_response_guidance.py`
- `STATUS.md`

## Limitacoes
- CLI local apenas
- sem endpoint administrativo
- sem workflow formal de aprovacao alem do versionamento

## Proximo passo
Adicionar uma etapa de proposta/revisao antes do `add/update`, ainda persistindo no mesmo `response_guidance.json`.
