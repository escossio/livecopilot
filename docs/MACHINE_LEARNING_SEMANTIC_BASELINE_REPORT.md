# MACHINE LEARNING Semantic Baseline Report

## Context
- Frente: MACHINE_LEARNING (estado `opened`, embeddings gerados na etapa anterior com `text-embedding-3-large`).
- Objetivo: avaliar a recuperação semântica das consultas oficiais usando os 8 vetores persistidos em `data/semantic_index_experiments/machine_learning/`.
- Queries processadas: as mesmas quatro referências do baseline lexical.

## Resultados por query

1. **what is overfitting in machine learning**
   - **Top1**: `crash_course-0001-a799aaf297d21c80` (score 0.313) — chunk contém a página principal do Machine Learning Crash Course, sem explicações longas, mas serve como ponto de entrada para o módulo "Datasets, generalization, and overfitting" citada no Top2.
   - **Top3**: `crash_course-0002-f779db68bb57add5` (score 0.283), `user_guide_html-0002-050d59c7447390fd` (score 0.273).
   - **Classificação**: PARCIAL (o índice retorna páginas oficiais alinhadas ao tópico, porém o conteúdo imediatamente disponibilizado é superficial e depende da navegação para encontrar o bloco dedicado ao overfitting).
   - **Lacunas**: ausência de um trecho textual direto explicando overfitting; o vetor precisa atravessar o TOC até o módulo correto.

2. **difference between supervised and unsupervised learning**
   - **Top1**: `user_guide_html-0002-050d59c7447390fd` (score 0.301) — seções de 1. Supervised learning e 2. Unsupervised learning aparecem no mesmo chunk, registrando ambas as categorias e subcapítulos.
   - **Top3**: `crash_course-0001-a799aaf297d21c80` (score 0.282), `crash_course-0002-f779db68bb57add5` (score 0.229).
   - **Classificação**: COERENTE (o chunk principal lista explicitamente as duas abordagens e oferece referências diretas a capítulos dedicados, então a resposta pode ser composta a partir das subseções listadas).
   - **Lacunas**: texto ainda é majoritariamente sumário/TOC, sem parágrafos narrativos longos sobre as diferenças.

3. **what is gradient descent**
   - **Top1**: `crash_course-0001-a799aaf297d21c80` (score 0.254) — página inicial do Crash Course com links gerais.
   - **Top3**: `crash_course-0002-f779db68bb57add5` (score 0.217), `guide-0001-a4648a6bd5198214` (score 0.201).
   - **Classificação**: PARCIAL (a maior parte dos vetores retorna páginas de navegação; somente o segundo e terceiro chunks começam a apontar para módulos sobre regressão linear e práticas do TensorFlow, mas os trechos imediatos ainda são títulos/TOCs).
   - **Lacunas**: falta de descrição coerente de como o gradient descent funciona e de seus elementos matemáticos no snippet imediato.

4. **what is a confusion matrix**
   - **Top1**: `user_guide_html-0001-11582df514d0025c` (score 0.221) — a guia do scikit-learn cobre classificadores e métricas, mas o trecho carregado não mostra o parágrafo sobre a matriz de confusão.
   - **Top3**: `guide-0001-a4648a6bd5198214` (score 0.198), `crash_course-0001-a799aaf297d21c80` (score 0.193).
   - **Classificação**: PARCIAL (há sinalização de métricas de classificação, mas o conteúdo retornado não apresenta a explicação específica da matriz de confusão nem seus eixos com taxas de verdadeiros/falsos positivos).
   - **Lacunas**: o primeiro conteúdo é indexado como documento geral; seria preciso navegar até a seção "Classification" para recuperar a definição completa.

## Decisão final
- O baseline registra uma **classificação geral PARCIAL**, pois as quatro consultas retornam páginas oficiais do ecossistema (Google Crash Course, scikit-learn e TensorFlow) porém, no nível do trecho carregado nos embeddings, prevalecem títulos e sumários em vez de paragrafos explicativos completos.
- Apesar da superficialidade, as páginas permanecem dentro do domínio correto; o próximo passo poderá enriquecer os chunks para capturar explicações completas semânticas.
- Esta rodada conclui o **semantic_baseline** sem avanço para `closure_decision`.

## Observações operacionais
- Embeddings das queries foram gerados com `text-embedding-3-large`.
- Similaridades calculadas por cosine similarity entre cada query e os 8 embeddings de chunk.
- Nenhuma etapa posterior (closure_decision, novos embeddings ou manipulação de corpus) foi executada.
