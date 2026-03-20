# status final
concluido

# comandos executados
- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,260p' STATUS.md`
- `sed -n '1,320p' app/services/response_guidance.py`
- `sed -n '321,520p' app/services/response_guidance.py`
- `sed -n '1,280p' tests/test_response_guidance.py`
- `sed -n '1,260p' data/response_guidance.json`
- `cp app/services/response_guidance.py app/services/response_guidance.py.bak.20260314T040115Z`
- `cp tests/test_response_guidance.py tests/test_response_guidance.py.bak.20260314T040115Z`
- `cp STATUS.md STATUS.md.bak.20260314T040115Z`
- `./.venv/bin/python -m py_compile app/services/response_guidance.py tests/test_response_guidance.py tests/test_response_guidance_proposals.py`
- `./.venv/bin/python -m unittest -v tests/test_response_guidance.py tests/test_response_guidance_proposals.py`

# arquivos tocados
- `app/services/response_guidance.py`
- `tests/test_response_guidance_proposals.py`
- `data/response_guidance_proposals/.gitkeep`
- `STATUS.md`

# o que foi alterado
- criada a estrutura `data/response_guidance_proposals/`
- adicionados os subcomandos CLI:
  - `propose`
  - `list-proposals`
  - `show-proposal`
  - `approve`
  - `reject`
- adicionada validacao de proposal em JSON com campos:
  - `proposal_id`
  - `status`
  - `created_at`
  - `proposed_rule`
- implementada aprovacao com insercao no `response_guidance.json`, preservando `version`
- implementada rejeicao sem apagar proposal
- adicionados backups timestampados antes de editar JSON existente
- mantida a CLI antiga intacta
- adicionados testes para criacao, aprovacao, rejeicao, duplicidade e integridade do JSON principal

# o que falta
- se a regra do processo exigir bloqueio total de escrita direta, falta migrar `add/update` para um modo somente-proposal
- se quiser revisao formal de alteracao em regra existente, falta um fluxo de proposal para `update`
- se quiser auditoria mais forte, faltam metadados de aprovador e motivo da decisao

# se precisa aprovacao
nao para este escopo tecnico implementado

# se houve erro
nao
