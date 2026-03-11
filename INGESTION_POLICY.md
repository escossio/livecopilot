# Ingestion Policy

## Mapeamento de camadas

- `source_indexes/` -> `data/source_indexes/`
- `source_candidates/` -> `data/source_candidates/`
- `knowledge/` -> `data/knowledge_raw/` + `data/knowledge_parsed/` + `data/knowledge_chunks/`
- `question_bank/` -> `data/question_bank_raw/` + `data/question_bank_parsed/` + `data/question_bank_items/`
- `coverage_inputs/` -> `data/coverage_inputs/`
- `question_bank_low_trust/` -> `data/question_bank_low_trust/`
- `raw_review/` -> `data/raw_review/`

## Regra principal

Indices curados e listas de links servem para descoberta. Eles nunca entram como conhecimento final nem como evidencia forte direta.

## Niveis de confianca

- `high_trust`: pode virar evidencia forte quando promovido para `knowledge`, `question_bank` ou `coverage_inputs`.
- `medium_trust`: pode entrar no nucleo apos promocao, mas nasce como nao-evidencia-forte por padrao.
- `curated_index`: descoberta apenas. Nunca conta como evidencia forte.
- `low_trust`: vai para revisao ou trilha de baixa confianca.
- `gray_source`: vai para revisao manual antes de qualquer promocao.

## Destinos

- `source_candidates`: fila de candidatos descobertos.
- `knowledge`: documentacao promovida para o nucleo.
- `question_bank`: material avaliativo promovido para o nucleo.
- `coverage_inputs`: insumos curados para coverage/action plan.
- `question_bank_low_trust`: material avaliativo util, mas com confianca baixa.
- `raw_review`: materiais que exigem triagem manual.

## Triagem manual minima

- Vai para `knowledge`: documentacao final, tutorial oficial ou guia tecnico confiavel com utilidade direta para responder perguntas do nucleo.
- Vai para `question_bank`: simulados, quizzes, bancos de questoes ou materiais avaliativos claramente estruturados.
- Vai para `coverage_inputs`: indices conceituais, referencias oficiais amplas, roadmaps e guias bons para mapear lacunas, mas nao ideais como evidencia final isolada.
- Vai para `raw_review`: fonte ambigua, agregador, post sem autoria clara, lista de links ou material que ainda exige confirmacao manual.
- Vai para `question_bank_low_trust`: material avaliativo util para descoberta de topicos, mas com confianca baixa ou origem editorial fraca.

## Regras operacionais

- Tipo real da fonte vem antes do rotulo do indice curado.
- Confianca alta ou media nao basta se a fonte for apenas indice, catalogo ou coletanea.
- Fonte final promovivel precisa ser mais que descoberta: precisa ter conteudo proprio e utilidade clara para `knowledge`, `question_bank` ou `coverage_inputs`.
- Em caso de duvida entre destino final e revisao, usar `raw_review`.

## Checklist manual de revisao

- Confirmar autoria e origem da fonte.
- Confirmar o tipo real da pagina ou arquivo.
- Confirmar se e fonte final ou apenas indice/agregador.
- Confirmar utilidade real para o nucleo.
- Confirmar confianca minima coerente com a origem.
- Confirmar se o destino esta correto: `knowledge`, `question_bank`, `coverage_inputs`, `raw_review` ou `question_bank_low_trust`.

## Campos persistidos

- `source_origin`
- `trust_level`
- `source_kind`
- `destination`
- `status`
- `parser_hint`
- `is_strong_evidence`

## Origem do candidato

- `web`: candidato descoberto por URL, lista externa ou recurso online.
- `local_file`: candidato que representa um artefato fisico ja presente na camada de curadoria.
- novos candidatos devem nascer com `source_origin` explicito.
- `register-candidate` aceita criacao por `--url` ou por `--artifact-path`; candidatos locais devem nascer com `source_origin=local_file`.
- inconsistencias de proveniencia aparecem no relatorio como alerta, mas nao bloqueiam o fluxo.
- no `report`, candidato sem `source_origin` entra em `candidate_summary.by_origin.web` por fallback conservador para manter a visao estavel em dados legados.
- esse fallback nao remove o alerta: o candidato continua aparecendo em `candidate_consistency.missing_source_origin`.

## Politica de evidencia

- `curated_index` nunca gera evidencia forte.
- `is_strong_evidence=false` deve rebaixar o uso em coverage.
- promocao para `knowledge`/`question_bank`/`coverage_inputs` exige classificacao previa; descoberta sozinha nao basta.

## Politica de duplicatas editoriais

- Variantes editoriais da mesma obra com o mesmo `identifier` devem ser tratadas como duplicata redundante.
- A regra padrao e manter um unico exemplar por `identifier`.
- Metadata mais limpa, titulo mais bonito ou descricao melhor nao justificam coexistencia por si so.
- Nesses casos, no maximo faz sentido uma futura normalizacao documental; nao um novo fluxo curatorial.
- Caso piloto validado: `Designing Distributed Systems`.
