# FRONT PYTHON

## Objetivo
- Formalizar a frente Python, governando o ciclo de vida completo da ingestão oficial (linguagem, standard library, packaging, async e CLI) antes de avançar para validações lexicais e semânticas.

## Escopo
- Domínio: linguagem Python, biblioteca padrão, packaging (pip, setuptools, packaging docs), async/await, tooling CLI (venv, python CLI flags) e scripting oficial.
- Exclusões: conteúdo de terceiros como blogs, tutoriais pagos, vídeos, fóruns e material opinativo sem origem oficial.

## Source policy
- Fontes permitidas: `docs.python.org` (Language Reference, Library Reference, Packaging Guide, HOWTOs oficiais) e subdomínios que carregam guias proprietários mantidos pela PSF.
- Conteúdo deve ser técnico, atualizado (sempre que possível indicar versão) e sem foco promocional.
- Idioma preferencial: inglês; material em outros idiomas só quando houver versão oficial traduzida pela PSF.
- Equipe deve evitar duplicações de versões antigas e priorizar o release `3.12`/`3.13`.

## Source manifest (inicial)
- Python Language Reference (`https://docs.python.org/3/reference/`) – Core syntax/semantics.
- Python Standard Library Reference (`https://docs.python.org/3/library/`) – módulos chaves (`asyncio`, `concurrent`, `os`, `sys`, `pathlib`).
- Packaging Guide (`https://packaging.python.org/en/latest/`) – pip, builds, publishing.
- AsyncIO docs (`https://docs.python.org/3/library/asyncio.html`) – event loop, tasks.
- CLI/Run-Time (`https://docs.python.org/3/using/cmdline.html`, `https://docs.python.org/3/using/windows.html`) – CLI flags, environment.

## Corpus lock (inicial)
- Scoped: versões oficiais indicadas acima, com foco no release ativo. Hashes e lotes serão congelados após a próxima etapa de corpus_preparation.
- Fora do lock: tutoriais não oficiais, posts de terceiros, conteúdo excessivamente orientado ao marketing.

## Status
- state: `closed`
- stage: `closure_decision`
- próximo passo: nenhuma etapa adicional; manter vigilância sobre novas releases oficiais.

## Lifecycle oficial
- Sequência completa documentada em `docs/FRONT_LIFECYCLE_CONTRACT.md`; a frente concluiu todas as etapas até `closure_decision`.

## Observação
- Todo processamento (parsing, chunking, embeddings) está pendente; esta etapa registra apenas o recorte documental.
