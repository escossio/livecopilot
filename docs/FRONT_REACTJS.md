# FRONT REACTJS

## Objetivo
- Abrir a frente ReactJS para formalizar a ingestão da documentação oficial e governar o ciclo de vida até o corpus_preparation.

## Escopo
- Domínio: React core, componentes, props/state, hooks, efeitos, renderização e fluxos recomendados pela documentação oficial do React.
- Exclusões: artigos de terceiros, blogs, cursos orientados a produtividade e implementações baseadas em bibliotecas não mantidas pela equipe do React.

## Source policy
- Fontes permitidas: `react.dev`, especialmente os capítulos sobre noções básicas, componentes, hooks e renderização.
- Conteúdo deve ser técnico, atualizado com as práticas do React atual (18+) e focado na API pública do framework.
- Evitar conteúdos promocionais, tutoriais de terceiros e implementações de bibliotecas proprietárias que estendam o React além da documentação oficial.

## Source manifest (inicial)
- React.dev Homepage (`https://react.dev/`) – visão geral, filosofia e links canônicos.
- React.dev Learn (`https://react.dev/learn`) – capítulos detalhados sobre componentes, props/state e hooks.
- React.dev API Reference (`https://react.dev/reference/react`) – referência oficial de APIs e hooks.

## Corpus lock (inicial)
- Scoped: as URLs acima e páginas derivadas vinculadas ao domínio `react.dev`.
- Fora do lock: blogs não oficiais, repositórios de terceiros e extensões experimentais do ecossistema.

## Status
- state: `closed`
- stage: `closure_decision`
- fechamento: final report e handoff registrados (`docs/REACTJS_FINAL_REPORT_20260319T191000Z.md`, `docs/HANDOFF_LIVECOPILOT_REACTJS_FRONT_CLOSURE_20260319T191000Z.md`).
- próximo passo: manter o índice para as queries React core e reabrir apenas se o escopo oficial mudar.

## Lifecycle oficial
- Pipeline completo documentado em `docs/FRONT_LIFECYCLE_CONTRACT.md`; esta frente começa em `corpus_preparation`.

## Observação
- Nenhuma ingestão nem parsing foi executado até o momento; o arquivo registra apenas escopo e estratégia.
