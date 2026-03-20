# HANDOFF: C Source Selection

## Contexto
- Segue o plano `docs/INGESTAO_C_EXECUTION_PLAN.md` e o princípio "official-first" do `docs/PROJECT_BRAIN.md`.
- Esta etapa evita ingestão e se concentra apenas em mapear o corpus inicial para linguagem C.

## O que foi feito
1. Avaliei oito candidatos (ISO/IEC 9899 C17, drafts WG14, The Open Group Base Specs, cppreference, man-pages, glibc, GCC/Clang docs e livros clássicos) usando critérios de oficialidade, clareza, densidade, risco editorial, facilidade de espelhamento e chunking.
2. Priorizei três categorias: normativo (C17 + drafts + POSIX Base Specs), secondary (cppreference + man-pages) e "não priorizar" (glibc, compiladores, livros). 
3. Propus um corpus piloto mínimo de cinco recursos (norma C17, WG14 draft, POSIX Base Specs, cppreference, man7 man-pages) garantindo fontes oficiais com suporte didático.
4. Documentei a política em `docs/C_OFFICIAL_SOURCE_POLICY.md`.

## Próximos passos recomendados
- Validar caminhos de aquisição/espelhamento para os PDFs ISO e POSIX (ex: WG14 downloads, The Open Group online).
- Criar um manifesto (manifest.json) com URLs e hashes para os cinco documentos do corpus antes da ingestão real.
- Planejar a próxima etapa: segmentação/chunking das primeiras seções (core language + stdlib) com atenção aos front matters.
