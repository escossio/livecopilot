# Handoff — Escopo e política de fontes do domínio Python (2026-03-17T03:25:06Z)

## Situação atual
- O método official-first validado no piloto C (documentado em `docs/C_PILOT_FINAL_REPORT.md`, na série de handoffs e no `STATUS.md` mais recente) será reaplicado agora para o domínio Python.
- Nesta rodada inicial foram analisadas as fontes oficiais, definido o recorte e registrada a política oficial-first em `docs/PYTHON_OFFICIAL_SOURCE_POLICY.md`; nenhum parsing, chunking nem ingestão foram iniciados.

## Escopo definido para o piloto Python
- Foco na linguagem base, built-ins, exceções e nos módulos essenciais para automação, serialização, CLIs, ambientes isolados e tipagem (`pathlib`, `subprocess`, `json`, `argparse`, `venv`, `pip`, `typing`).
- O escopo evita a biblioteca padrão inteira, adiando módulos complexos (ex.: `asyncio`, `socket`, coleções avançadas) e frameworks de terceiros.
- A definição privilegia um domínio manejável que responde perguntas reais de operações sem encher o índice global.

## Política de fontes oficiais
- Prioridade máxima para a documentação oficial mantida pela Python Software Foundation (`docs.python.org/3`), cada módulo citado em `docs/PYTHON_OFFICIAL_SOURCE_POLICY.md` e a documentação oficial do pip (`pip.pypa.io`).
- Fontes secundárias autorizadas (PEPs selecionadas, Packaging User Guide) são citadas apenas quando esclarecem comportamentos do escopo inicial.
- Conteúdos informais (blogs, StackOverflow, livros, cursos gratuitos) foram explicitamente excluídos na política.

## Próximos passos sugeridos (manifesto operacional das fontes)
1. Consolidar o manifesto operacional: listar cada URL prioritária, versão/clone, escopo e responsável antes de qualquer download ou chunking.
2. Validar a bateria curta de perguntas-chave para os tópicos listados, como foi feito para `<assert.h>` e `read()` no piloto C, garantindo que o recorte inicial responde o esperado.
3. Planejar a estrutura isolada (`data/knowledge_domains/python/...`, metadata e scripts de consulta) para manter o domínio separado do índice global.
4. Reunir o time para revisar a política official-first antes de permitir parsing e chunking, evitando qualquer mistura de domínios ou fontes secundárias fora do manifesto.
