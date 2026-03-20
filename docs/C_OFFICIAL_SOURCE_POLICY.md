# C Official Source Policy

Este artefato registra a seleção inicial de fontes oficiais/canônicas para a frente "official-first" de ingestão da linguagem C do LiveCopilot.
Ele é um desdobramento direto do plano em `docs/INGESTAO_C_EXECUTION_PLAN.md` e assume os princípios descritos em `docs/PROJECT_BRAIN.md` (Knowledge First, Official Sources Priority, Operational Discipline).

## Critérios de avaliação
- **Oficialidade:** documento vinculado a um organismo formal (ISO, IEEE, The Open Group) ou reconhecido internacionalmente pela comunidade C.
- **Clareza técnica:** linguagem objetiva, estrutura lógica e presença de exemplos/definições que respondem a questões conceituais.
- **Densidade semântica:** informação respondivel para perguntas conceituais sobre o núcleo da linguagem ou da biblioteca padrão.
- **Risco editorial:** grau de interpretação/viés autoral. Prioriza-se texto normativo ou editorialmente neutro.
- **Facilidade de clonagem/espelhamento:** disponibilidade em repositório oficial ou acesso direto via URL aberta.
- **Ajuste para chunking limpo:** se o documento já tem divisões claras (seções, tabelas, marcadores) e ausência excessiva de propaganda.

## Fontes candidatas avaliadas
1. **ISO/IEC 9899:2018 (C17) — Normativo oficial**
   - Oficialidade: máxima (ISO). Processo de aprovação final do WG14.
   - Clareza: formal, mas segmentado em capítulos (introdução, lexemas, semantics). Requer leitura cuidadosa, mas cada seção aplica definições precisas.
   - Densidade: alta (define sintaxe, atributos, biblioteca padrão).
   - Risco editorial: quase nulo.
   - Clonagem: arquivo pago, mas há espelhos liberados pelo WG14 (e.g., N2610) que reproduzem o texto praticamente sem perdas.
   - Chunking: em capítulos, tabelas, anexos; ideal para dividir em pedaços normativos.

2. **Drafts públicos do WG14 (p. ex. N2610 — final draft de C17, N2756 — C23)**
   - Oficialidade: muito alta; documentos mantidos pelo comitê.
   - Clareza: já estão próximos do texto normativo final e incluem notas explicativas.
   - Densidade: idem acima, porém com o benefício de comentários orientadores.
   - Risco editorial: baixo; apesar de conter trechos de discussão, continuam técnicos.
   - Clonagem: PDF disponível gratuitamente no site do WG14.
   - Chunking: seções numeradas, ideal para ingestão incremental e para anexos específicos (como anexos sobre biblioteca).

3. **The Open Group Base Specifications Issue 7 (POSIX.1-2017)**
   - Oficialidade: alta (IEEE/ The Open Group). Cobre muitas APIs de C utilizadas em ambientes Unix.
   - Clareza: formato técnico claro, com descrições de funções, parâmetros, exemplos de efeitos.
   - Densidade: altíssima para APIs, flags e comportamentos esperados.
   - Risco editorial: baixo; é um padrão industrial, sem opinião.
   - Clonagem: HTML/PDF online (`pubs.opengroup.org`).
   - Chunking: estrutura em capítulos e subseções com tabelas, facilita extrair funções individuais.

4. **Cppreference — seção C (language + library)**
   - Oficialidade: secundária (projeto comunitário), mas usa citações diretas da ISO.
   - Clareza: excelente para desenvolvedores, com exemplos e notas de compatibilidade.
   - Densidade: altíssima para perguntas práticas e comparações.
   - Risco editorial: moderado, pois há comentários comunitários, mas curados.
   - Clonagem: HTML estável, possível espelhar snapshots (via GitHub mirror `cppreference/cppreference`).
   - Chunking: cada página é curta e dividida por tópicos.

5. **Man-pages Linux / libc (man7.org)**
   - Oficialidade: moderada (mantido pela comunidade man-pages, mas bem aceita como referência de sistema).
   - Clareza: focada em uso prático de APIs, comportamento de funções.
   - Densidade: boa para funções POSIX, mas menos útil para gramática da linguagem.
   - Risco editorial: baixo.
   - Clonagem: repositório GitHub `man-pages/man-pages`.
   - Chunking: texto já estruturado em seções (descrição, opções, exemplos).

6. **Glibc manual (seção C reference)**
   - Oficialidade: específica para glibc.
   - Clareza: descreve implementações reais e flags.
   - Densidade: alta para comportamentos reais, mas pode conflitar com outras bibliotecas.
   - Risco editorial: médio (implementação-focused).
   - Clonagem: Git (https://sourceware.org/git/?p=glibc.git;a=summary).
   - Chunking: seções em HTML.

7. **Documentação de compiladores (GCC C Language Dialect, Clang Language Reference)**
   - Oficialidade: baixa; é mais um guia de suporte a dialetos do compilador.
   - Clareza: boa para extensão de recursos.
   - Densidade: boa, mas orientada a extensões/compatibilidade.
   - Risco editorial: mais alto (explica comportamento específico do compilador).
   - Clonagem: site oficial.
   - Chunking: seções, mas mistura features proprietárias.

8. **Livros clássicos/sketches (K&R, etc.)**
   - Oficialidade: nenhuma.
   - Clareza: excelente, mas editorial.
   - Densidade: moderada.
   - Risco editorial: alto (estilo autoral e datado).
   - Clonagem: não gratuito.

## Recomendação priorizada
### FONTE_PRIMARIA
- **ISO/IEC 9899:2018 (C17)** e **drafts oficiais WG14 (N2610/N2756)** — serve como núcleo normativo. Usar capítulos 1–7 e anexos essenciais para linguagem e biblioteca padrão.
- **The Open Group Base Specifications Issue 7** — complementa o padrão C com comportamentos POSIX exigidos em deploys reais.
  - Justificativa: disponibilidade pública, alcance legal e foco em APIs que o corpus precisa explicitar.
  - Como usar: extrair funções (e.g., <stdio.h>, <pthread.h>), incluindo as descrições, efeitos e requisitos.

### FONTE_SECUNDARIA
- **Cppreference (seção C language + library)** — serve como verniz didático e cross-check (explica erros comuns, comparações e exemplos).
  - Pode ser consumida após o vínculo com as fontes primárias para validar clareza e preencher links faltantes.
- **Man-pages Linux / libc (man7.org)** — oferece descrição de comportamentos práticos, flags e exemplos para funções POSIX/C; útil para ancorar respostas de implementação.

### NAO_PRIORIZAR_AGORA
- **Glibc manual** — útil apenas quando houver dúvidas sobre comportamento específico; evita misturar com o corpus principal nesta etapa.
- **Documentação de compiladores (GCC/Clang)** — fica para fases posteriores, se surgir necessidade de lidar com dialetos ou extensões.
- **Livros e blogs (K&R, etc.)** — não entram no piloto por serem editorialmente pesados e menos atualizados.

## Corpus piloto mínimo sugerido
1. **C17 core (ISO/IEC 9899:2018)** — seções 1–7, anexos A e B (lexemas, tipos, statements, functions), distribuídos como PDFs ou texto estruturado; manter cópia local ou em mirror autorizado.
2. **Draft WG14 N2610 (C17) ou N2756 (C23)** — usar para ter acesso aberto ao mesmo conteúdo e às notas; permite chunking por preenchimento de seções e comentários.
3. **The Open Group Base Specs (Issue 7)** — incluir capítulos 2 e 4 (definições, funções) para API POSIX; especialmente `stdio.h`, `stdlib.h`, `pthread.h` e `unistd.h`.
4. **Cppreference C language + library** — espelhar a seção `https://en.cppreference.com/w/c/language` e `https://en.cppreference.com/w/c/header` como HTML estável para cross-reference.
5. **Man-pages (man7.org)** — focar nos capítulos 2 e 3 relevantes (system calls e library calls) complementares às funções da biblioteca padrão.

Esse corpus mantém o piloto pequeno (5 fontes), combina normativo com material explicativo acessível e garante que cada chunk seja ancorado em seções oficiais ou curadas, facilitando o ranking semântico.
