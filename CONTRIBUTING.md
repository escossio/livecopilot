# Contributing to Livecopilot

## 1. Preparar ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Opcional:

```bash
cp .env.example .env
```

## 2. Rodar testes

Gate padrao local:

```bash
scripts/unit_test_gate.sh
```

Se o gate falhar, corrija a causa com a menor mudanca possivel antes de abrir PR.

## 3. Propor mudancas

- Crie branch com nome claro por frente.
- Mantenha escopo pequeno e auditavel.
- Atualize documentacao relevante quando alterar comportamento.
- Registre checkpoint em `STATUS.md` quando concluir etapa relevante.

## 4. Convencoes minimas

- Nao inventar capacidades no README/docs.
- Preferir alteracoes pequenas e reversiveis.
- Evitar dependencias novas sem necessidade real.
- Preservar evidencias operacionais em `docs/` quando a mudanca for de fluxo.
