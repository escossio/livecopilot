# HANDOFF: C Source Manifest & Ingestion Order

## Contexto
- Desdobramento da política registrada em `docs/C_OFFICIAL_SOURCE_POLICY.md` e continuidade de `docs/HANDOFF_LIVECOPILOT_C_SOURCE_SELECTION_20260315T083000Z.md`.
- Objetivo desta rodada: transformar a política em um manifesto executável, fixando URLs, formatos e prioridades antes de qualquer ingestão.

## Manifesto gerado
- Arquivo principal: `docs/C_SOURCE_MANIFEST.md` com tabela de cinco fontes (ISO/C17, WG14 drafts, POSIX Issue 7, cppreference, man7) descrevendo categoria, tipo, URIs, acesso e estratégia de coleta.
- Artefato secundário: `docs/C_SOURCE_MANIFEST.json` com os mesmos metadados (nome curto, categoria, batch, prioridade, estratégias) para consumo por scripts de ingestão.

## Ordem recomendada de ingestão
1. **Lote 1** – ISO/IEC 9899:2018 (com espelho WG14) e The Open Group Base Specifications Issue 7. Serve para garantir a base normativa e as APIs POSIX primordiais.
2. **Lote 2** – Progressão dentro do mesmo POSIX Issue 7 para capítulos restantes de biblioteca padrão e funções críticas.
3. **Lote 3** – fontes secundárias (cppreference e man7) para enriquecer com exemplos, notas práticas e flags, após o lote 1 ter sido arquivado localmente.

## Riscos/licenças/acesso
- O ISO 9899:2018 exige compra da norma, portanto usar o espelho WG14 (N2610) até o pagamento ser concluído e armazenar o recibo/licença.
- Os drafts WG14 e The Open Group são gratuitos, mas exigem controle de versão para detectar novas revisões antes que o manifest vá para ingestão.
- cppreference exige atribuição CC BY-SA; man7/man-pages está sob GPL.

## Próximo passo sugerido
Validar downloads (pdf/HTML) para cada entrada, registrar hashs em `data/knowledge_raw/c/manifest-hashes.json` e só então iniciar parsing/chunking seguindo os lotes anotados no manifesto.
