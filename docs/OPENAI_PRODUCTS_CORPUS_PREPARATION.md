# OPENAI_PRODUCTS – Corpus Preparation

## Estratégia de ingestão (recorte técnico)
- Priorizar páginas oficiais da OpenAI (docs.openai.com, platform.openai.com, developers.openai.com, help.openai.com, openai.com/blog/index) com conteúdo técnico de referência ou guias.
- Recorte focado: APIs, modelos, embeddings, realtime, audio, images, limites/políticas, e toda a superfície oficial de CODEX (app/CLI/IDE/prompting/changelog/modelos).
- Excluir qualquer material promocional ou não técnico mesmo em domínios oficiais (posts puramente de marketing sem detalhes de uso).

## Tipos de conteúdo permitidos
- Referências de API (REST/SDK), esquemas de requisição/resposta, autenticação, erros, rate limits.
- Especificações de modelos (context window, capacidades, parâmetros).
- Guias oficiais (embeddings, realtime, audio, images, prompting).
- Changelogs e release notes técnicos.
- Artigos de ajuda oficiais quando detalham comportamento ou configurações (ex.: uso de Codex em planos).
- Posts técnicos oficiais do blog com detalhes operacionais de produtos/modelos.

## Tipos de conteúdo proibidos
- Tutoriais de terceiros, vídeos, cursos, fóruns.
- Artigos opinativos ou de marketing sem detalhes técnicos acionáveis.
- Conteúdo não oficial ou fora dos domínios aprovados.

## Estrutura do corpus (raw)
- `data/knowledge_raw/openai/api` – referências e guias de API.
- `data/knowledge_raw/openai/models` – docs de modelos e especificações.
- `data/knowledge_raw/openai/codex` – conteúdo oficial Codex (app, CLI, IDE, prompting, changelog, help).
- `data/knowledge_raw/openai/policies` – limites, pricing, rate limits, termos de uso aplicáveis.

## Workflow de ingestão
1) Selecionar URLs aprovadas do corpus_lock/manifest e mapear para as pastas acima.
2) Fazer fetch estático (HTML/MD) mantendo metadados de URL e data.
3) Normalizar para texto bruto (limpar navegação, TOCs, scripts).
4) Registrar manifest de materialização (fonte, URL, data, destino).
5) Freeze do raw antes de parsing/chunking.
6) Somente depois seguir para parsing/chunking, mantendo rastreabilidade por arquivo e URL.
