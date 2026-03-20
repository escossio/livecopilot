# Política de Fontes Oficiais — Domínio Python (2026-03-17T03:25:06Z)

## Objetivo do domínio Python
- replicar o método official-first validado pelo piloto C (`docs/C_PILOT_FINAL_REPORT.md` e `docs/HANDOFF_LIVECOPILOT_C_PILOT_CLOSURE_20260317T180000Z.md`): isolar o domínio, priorizar documentação oficial e preparar um pipeline que só será acionado após o manifesto inicial.
- gerar um escopo útil e contido que permita perguntas sobre sintaxe, funções, exceções e módulos críticos sem tocar o índice global ou iniciar parsing/ingestão.

## Recorte inicial do piloto
1. **Linguagem base** (gramática, tipagem dinâmica, modelo de execução): garante respostas sobre sintaxe, expressões e comportamento do interpretador.
2. **Funções built-in e exceções** (`library/functions.html`, `library/exceptions.html`): cobre o repertório de operações fundamentais e o tratamento de erros.
3. **Módulos alvo:**
   - `pathlib`: manipulação de arquivos e diretórios com API moderna.
   - `subprocess`: execução e controle de processos externos, essencial para automações e scripts operacionais.
   - `json`: serialização/deserialização padrão para integração com APIs e logs.
   - `argparse`: construção de CLIs oficiais e parsing consistente de argumentos.
   - `venv`: criação de ambientes isolados, etapa preparatória para controles de dependência.
   - `pip`: instalação e atualização de pacotes, referência oficial em `pip.pypa.io`.
   - `typing`: anotações opcionais e suporte a ferramentas de verificação, alinhado com o manifesto de tipos do Python 3.x.
4. **Contexto operacional:** foco em documentos que descrevem o interpretador CPython 3.x atual e as operações que a equipe responde diariamente; evita abrangência total da biblioteca padrão logo no início.

## Fontes avaliadas
### FONTE_PRIMARIA
- `https://docs.python.org/3/`: tutorial oficial, language reference e library reference (todos mantidos pelo Python Software Foundation).
- `https://docs.python.org/3/reference/`: gramática, modelo de execução e comportamento do interpretador.
- `https://docs.python.org/3/library/functions.html` e `https://docs.python.org/3/library/exceptions.html`: built-ins e tratamento de erros.
- Cada página de módulo citado (`pathlib`, `subprocess`, `json`, `argparse`, `venv`, `typing`) dentro de `docs.python.org/3/library/`.
- `https://pip.pypa.io/en/stable/` (documentação oficial do projeto pip) para comandos, uso em scripts e interações com `venv`.

### FONTE_SECUNDARIA
- `https://www.python.org/dev/peps/pep-0484/` e `https://www.python.org/dev/peps/pep-0585/` quando precisarmos justificar comportamentos de typing por trás das dataclasses e genéricos.
- `https://packaging.python.org/` como referência oficial suplementar para resolver dúvidas sobre instalação e ambientes que dependem de pip/venv juntos.
- Outras PEPs relevantes apenas se refinarem o entendimento de um módulo já incluído (ex.: PEP 584 para operadores em typing) — não serão fontes principais, mas oferecem contexto autorizado.

### NAO_PRIORIZAR_AGORA
- Blogs, Medium, posts aleatórios, StackOverflow, livros e cursos (a não ser que vire material oficial revisado pelo PSF).
- Documentação de versões anteriores (Python 2.x ou ramos antigos) salvo comparação explícita.
- Repositórios de terceiros e posts de comunidade que não passem pelo crivo oficial do Python Software Foundation.

## O que entra agora
- Explicações oficiais sobre a linguagem base, built-ins e o ecossistema de exceções (resposta a perguntas sobre sintaxe, conversão, manipulação de erros e fluxo).
- Guias oficiais de cada módulo alvo com exemplos e recomendações concretas (pathlib, subprocess, json, argparse, venv, pip, typing).
- Tutorial oficial do Python (`docs.python.org/3/tutorial/`) para cobrir padrões idiomáticos e boas práticas aceitas.
- Referências diretas a pip e packaging para contextos operacionais (instalação, atualizações e compatibilidade entre ambientes).

## O que fica fora
- Frameworks completos (Django, Flask, FastAPI), bibliotecas científicas e outras camadas altas.
- Módulos da biblioteca padrão não mencionados no recorte inicial (por exemplo `asyncio`, `socket`, GUI ou coleções avançadas) até que a primeira etapa seja validada.
- Conteúdo extraoficial como notas de blogs, StackOverflow, vídeos ou cursos.
- A ingestão completa de pacotes PyPI além do pip/venv descrito acima; isso aguarda manifestação operacional posterior.

## Riscos e limitações
- Cobertura limitada significa que perguntas sobre outros módulos (collections, os, threading, etc.) ficarão de fora até a etapa de expansão.
- Documentação oficial é volumosa; precisamos evitar chunking indiscriminado e focar nos tópicos listados.
- A versão alvo (CPython 3.11/3.12) pode evoluir, logo o manifesto precisará de revisões periódicas para evitar content drift.
- Esse recorte depende de um manifesto consolidado antes de qualquer parsing, chunking ou ingestão.

## Próximos passos
1. Criar o manifesto operacional de fontes (lista oficial com URLs, hashes e escopo de cada documento) para garantir que o pipeline official-first seja reproduzível.
2. Planejar a bateria inicial de perguntas-chave para cada módulo e para o modelo de linguagem base, como feito no piloto C antes do refinamento de `<assert.h>` e `read()`.
3. Definir a estrutura de domínio isolado (`data/knowledge_domains/python/<subdominio>`), scripts de consulta e checkpoints, mantendo o índice global intacto.
4. Validar internamente que a política official-first é compreendida por toda a equipe antes de acionar qualquer parsing, chunking ou geração de embeddings.
