# MACHINE LEARNING — Corpus Preparation

## Estratégia de corpus
- Priorizar capturas oficiais de documentação e guias de referência que descrevem algoritmos clássicos, pipelines de experimentos e APIs de frameworks, mantendo separação clara entre teoria e exemplos práticos.
- Registrar cada captura com a data, versão e taxonomy para permitir rastreamento antes de prosseguir para parsing e chunking.

## Conteúdos permitidos
- Documentação oficial de bibliotecas (scikit-learn, PyTorch, TensorFlow) e guias de referência do Google Machine Learning Crash Course.
- Seções de API, tutoriais práticos, notas de release relevantes e recomendações de melhores práticas das equipes mantenedoras.
- Conteúdo que explique pipelines de treinamento, inferência, avaliação, tuning e deploy dentro dos domínios acima.

## Conteúdos proibidos
- Tutoriais de terceiros, posts de blogs, vídeos, materiais pagos, fóruns (Stack Overflow, Reddit) e conteúdos sem rastreabilidade oficial.
- Estudos de caso proprietários, marketing de fornecedores que não estejam publicados nos domínios autorizados e recursos que tratem apenas de MLOps generalista sem relação direta com o ciclo dos frameworks oficiais.
- Fragmentos de código sem contexto explicativo ou referências a versões não mantidas pelas equipes oficiais.

## Estrutura esperada do raw
- Diretório raíz: `data/knowledge_raw/machine_learning/`.
- Subdiretórios organizados por fonte e categoria, ex.: `data/knowledge_raw/machine_learning/scikit-learn/api/`, `.../tensorflow/tutorials/`, `.../pytorch/release_notes/`, `.../google_ml_crash_course/concepts/`.
- Arquivos preferencialmente em Markdown/HTML limpo; cada captura deve manter o nome original e incluir um manifesto de metadados ao lado (JSON com mesma base de nome).

## Regras de metadados
- Campos obrigatórios: `source_url`, `capture_date` (ISO 8601), `framework_version` ou tag equivalente, `authoring_team` (ex: Scikit-Learn Steering Committee) e `hash` (SHA256 da versão capturada).
- Incluir `content_category` (API, tutorial, release, conceptual guide) e `language` (ex: en-US) para facilitar filtragem durante o parsing.
- Referenciar o `docs/MACHINE_LEARNING_SOURCE_MANIFEST.json` correspondente para garantir validade das URLs e dominio autorizado.

## Domínios autorizados
- `scikit-learn.org`
- `pytorch.org`
- `tensorflow.org`
- `developers.google.com`
- Domínios oficiais adicionais mantidos diretamente pelas equipes desses projetos podem ser considerados caso deem suporte ao material principal listado acima.
