# REACTJS Lexical Baseline Report

## Objetivo
- Confirmar que as consultas sobre hooks, estado e renderização priorizam chunks oficiais do ReactJS.

## Resultados

### 1. Query: `react useEffect lifecycle`
- **Top1:** `react_dev_api_reference-0002-1dd4b50a2fc0067d` (`react_dev_api_reference.html`, score 38)
- **Top3:** inclui `react_dev_homepage-0005-28ff4421c6dd2b28` (28) e `react_dev_learn-0002-478c57b797b65940` (27)
- **Domínio correto:** REACTJS

### 2. Query: `react useState example`
- **Top1:** `react_dev_learn-0002-478c57b797b65940` (`react_dev_learn.html`, score 50)
- **Top3:** `react_dev_api_reference-0002-...` (39), `react_dev_homepage-0005-...` (28)
- **Domínio correto:** REACTJS

### 3. Query: `react component rendering`
- **Top1:** `react_dev_learn-0002-478c57b797b65940` (score 58)
- **Top3:** `react_dev_api_reference-0002-...` (54), `react_dev_homepage-0005-...` (32)
- **Domínio correto:** REACTJS

### 4. Query: `react hooks rules`
- **Top1:** `react_dev_api_reference-0002-1dd4b50a2fc0067d` (score 54)
- **Top3:** `react_dev_learn-0002-...` (35), `react_dev_homepage-0005-...` (28)
- **Domínio correto:** REACTJS

## Observações
- O baseline lexical retorna consistentemente chunks do front ReactJS para as quatro consultas, atendendo ao critério de top1/top3 esperados.
