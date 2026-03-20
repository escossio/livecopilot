# Manifesto Operacional de Fontes — Domínio Python (2026-03-17T04:20:00Z)

## Contexto
- Esse manifesto transforma a política official-first documentada em `docs/PYTHON_OFFICIAL_SOURCE_POLICY.md` em instruções executáveis, sem começar o download, parsing ou chunking.
- O objetivo é ter URLs, categorias, estratégias e lotes definidos para o escopo controlado (linguagem base + built-ins/exceptions + módulos `pathlib`, `subprocess`, `json`, `argparse`, `venv`, `pip`, `typing`).
- O método aplicado é o mesmo do piloto C encerrado em `docs/C_PILOT_FINAL_REPORT.md`, portanto mantemos o domínio isolado e priorizamos fontes oficiais antes de qualquer contato com o índice global.

## Fontes confirmadas
### 1. Python Tutorial oficial (PSF)
- Nome canônico: Python Tutorial
- Categoria: PRIMARIA
- Tipo: GUIDE
- URL principal: https://docs.python.org/3/tutorial/
- URL espelho: https://docs.python.org/3/tutorial/index.html
- Disponibilidade prática: online, publicado pelo PSF em HTML estático, fácil de baixar via `wget` e versionar pelo timestamp da compilação.
- Observações de licença/acesso: Python Software Foundation License (aprovada para redistribuição interna e ingestão).
- Estratégia de coleta: snapshot HTML (mirroring do site) e registro do índice `/3/tutorial/index.html` para evitar mudanças inesperadas.
- Prioridade de ingestão: 1
- Lote sugerido: Lote 1

### 2. Language Reference oficial
- Nome canônico: Python Language Reference
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/reference/
- URL espelho: https://docs.python.org/3/reference/index.html
- Disponibilidade prática: online, mantido pelo PSF com poucas mudanças por release; útil para gramática e modelo de execução.
- Observações de licença/acesso: PSF License.
- Estratégia de coleta: congelar o índice e baixar os capítulos relevantes (lexical, execution model) para evitar content drift.
- Prioridade: 1
- Lote: Lote 1

### 3. Built-in Functions Reference
- Nome canônico: Built-in Functions
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/functions.html
- URL espelho: https://docs.python.org/3/library/functions.html#built-in-functions
- Disponibilidade prática: página única, mantida pela PSF.
- Observações: PSF License, nenhuma autenticação.
- Estratégia: baixar como HTML, registrar hash e metadados.
- Prioridade: 1
- Lote: Lote 1

### 4. Exception Hierarchy Reference
- Nome canônico: Built-in Exceptions
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/exceptions.html
- URL espelho: https://docs.python.org/3/library/exceptions.html#exception-hierarchy
- Disponibilidade: online, referência única.
- Estratégia: mirror + hash, garantir que a hierarquia esteja consistente entre releases.
- Prioridade: 1
- Lote: Lote 1

### 5. Módulo pathlib
- Nome canônico: pathlib
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/pathlib.html
- URL espelho: https://docs.python.org/3/library/pathlib.html#pathlib
- Disponibilidade: documento oficial, atualizado com cada release.
- Observações: cobrir uso prático de path objects, Path.home, etc.
- Estratégia: baixar página e subseções, mapear exemplos.
- Prioridade: 1
- Lote: Lote 1

### 6. Módulo subprocess
- Nome canônico: subprocess
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/subprocess.html
- URL espelho: https://docs.python.org/3/library/subprocess.html#subprocess-programs
- Disponibilidade: online, com exemplos de chamadas/arquitetura.
- Estratégia: baixar seções de `run`, `Popen`, `PIPE`, `timeout`.
- Prioridade: 1
- Lote: Lote 1

### 7. Módulo json
- Nome canônico: json
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/json.html
- URL espelho: https://docs.python.org/3/library/json.html#module-json
- Disponibilidade: online, PSF.
- Estratégia: capturar seções de `dump`, `loads`, `JSONEncoder`, `JSONDecoder`.
- Prioridade: 1
- Lote: 1

### 8. Módulo argparse
- Nome canônico: argparse
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/argparse.html
- URL espelho: https://docs.python.org/3/library/argparse.html#argparse-module
- Disponibilidade: online, PSF.
- Estratégia: salvar seções sobre `ArgumentParser`, subparsers, custom actions e exemplos recomendados.
- Prioridade: 1
- Lote: 1

### 9. Módulo venv
- Nome canônico: venv
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/venv.html
- URL espelho: https://docs.python.org/3/library/venv.html#module-venv
- Disponibilidade: online, PSF.
- Estratégia: capturar instruções de criação/ativação e limpezas recomendadas.
- Prioridade: 1
- Lote: 1

### 10. Módulo typing
- Nome canônico: typing
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://docs.python.org/3/library/typing.html
- URL espelho: https://docs.python.org/3/library/typing.html#typing
- Disponibilidade: online, PSF, atualizado com novas sugestões de generics.
- Estratégia: focar em `Annotated`, `TypedDict`, `Protocol`, `type aliases`.
- Prioridade: 1
- Lote: 1

### 11. pip oficial
- Nome canônico: pip
- Categoria: PRIMARIA
- Tipo: HTML
- URL principal: https://pip.pypa.io/en/stable/
- URL espelho: https://pip.pypa.io/en/stable/cli/pip_install/
- Disponibilidade: site oficial do PyPA, licenciado sob MIT.
- Estratégia: registrar comandos principais (`install`, `list`, `freeze`, `wheel`, `venv`), versões compatíveis e melhores práticas com venv.
- Prioridade: 2
- Lote: Lote 2

### 12. Packaging User Guide
- Nome canônico: Packaging User Guide
- Categoria: SECUNDARIA
- Tipo: GUIDE
- URL principal: https://packaging.python.org/
- URL espelho: https://packaging.python.org/en/latest/
- Disponibilidade: maintained pelo PyPA, MIT.
- Estratégia: capturar seções sobre ambientes virtuais, arquivos `pyproject.toml`, e distribuição preventiva.
- Prioridade: 2
- Lote: Lote 2

### 13. PEP 484 (Typing)
- Nome canônico: PEP 484
- Categoria: SECUNDARIA
- Tipo: PEP
- URL principal: https://peps.python.org/pep-0484/
- URL espelho: https://www.python.org/dev/peps/pep-0484/
- Disponibilidade: documento oficial do PSF.
- Estratégia: registrar definições de anotações de tipos, `typing` vs `collections.abc`.
- Prioridade: 3
- Lote: Lote 3

### 14. PEP 585 (Typing generics)
- Nome canônico: PEP 585
- Categoria: SECUNDARIA
- Tipo: PEP
- URL principal: https://peps.python.org/pep-0585/
- URL espelho: https://www.python.org/dev/peps/pep-0585/
- Disponibilidade: oficial, descreve generics nativos.
- Estratégia: foco em uso de `list[int]`, `dict[str, Any]`, compatibilidade com typing module.
- Prioridade: 3
- Lote: Lote 3

## Ordem de ingestão e racional
- **Lote 1 (Linguagem e módulos essenciais)**: tutorial, language reference, built-ins/exceptions e os seis módulos críticos. Esses registros dão fundação para perguntas operacionais e permitem validar o domínio antes de afetar o índice global.
- **Lote 2 (pip + packaging)**: foca em como instalar/gerenciar ambientes e dependências, o que depende do conhecimento do lote 1.
- **Lote 3 (PEPs)**: traz contexto adicional sobre typing, mas só entra após o lote 1 e 2 atenderem às questões imediatas da equipe.

## Fontes adiadas / riscos
- As PEPs entram no lote 3 porque não são necessárias para responder questões básicas de operação; além disso, elas referenciam o typing module e dependem de uma base estável dos outros documentos antes de serem interpretadas.
- O volume do `language reference` e do tutorial exige cuidado para evitar redundância (muitos capítulos cobrem o mesmo assunto com profundidade diferente). A estratégia é focar nos capítulos ligados ao escopo e evitar chunking desnecessário de seções fora do recorte.
- As atualizações nas doc oficial e no pip podem gerar content drift; logar timestamps e hashes evita ingestões inconsistentes.
- Ainda não são contempladas fontes extras (ex.: `os`, `threading`, frameworks) para manter o domínio limitado.

## Próximos passos sugeridos
1. Validar que cada URL pode ser acessada pela equipe (ping/site check) antes de baixar.
2. Registrar o manifesto em formato JSON (`docs/PYTHON_SOURCE_MANIFEST.json`) para que scripts possam orquestrar lotes automaticamente.
3. Planejar o lote 1 como o próximo freeze parcial: criar checkpoints antes de iniciar downloads.
4. Manter o status documentado até que o manifesto seja aprovado e o freeze seja autorizado.
