# Python Corpus Preparation

## Estratégia de ingestão
- Capturar versões oficiais da documentação Python (Language Reference, Library Reference, Packaging Guide, AsyncIO, CLI) com foco no release ativo (`3.12`/`3.13`).
- Priorizar páginas canonizadas no domínio `docs.python.org`, mantendo metadados de versão e SHA para rastreio.
- Assegurar arquivos convertidos para markdown puro mantendo headings e atributos `id` correspondentes.

## Tipos de conteúdo permitidos
- Textos técnicos sobre sintaxe, built-ins, módulos da biblioteca padrão relevantes ao escopo definido (`asyncio`, `concurrent`, `os`, `sys`, `pathlib`).
- Guias de packaging oficiais (`packaging.python.org`), CLI/uso da linha de comando e melhores práticas de scripting.
- Referências de configuração de ambientes virtuais, pip, pyproject e deployments oficiais.

## Tipos de conteúdo proibidos
- Tutoriais independentes, vídeos, cursos pagos, blogs não oficiais, posts promocionais e conteúdos duplicados que não tragam valor adicional oficial.
- Conteúdos de distribuidores (ex.: Debian packaging notes) que não sejam parte direta do repositório oficial mantido pelo PSF.

## Estrutura do corpus
- Diretório: `data/knowledge_raw/python/`
- Subdivisões esperadas (exemplos): `language/`, `library/`, `packaging/`, `async/`, `cli/`.
- Cada arquivo será convertido para markdown e normalizado com metadados `source_url`, `captured_at` e `hash`.

## Workflow de ingestão
1. Listar recursos aprovados (language reference, library, packaging, async, CLI) e capturar HTML/markdown localmente.
2. Normalizar e traduzir para markdown técnico preservando títulos e IDs.
3. Registrar cada artefato no corpus lock (path, hash, URL) antes de proceder ao parsing.
4. Documentar eventuais adiamentos ou fontes substitutas no arquivo de manifest e no STATUS.
