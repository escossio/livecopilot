# Chunk Quality Summary 20260315T202728Z

## Key observations
- The semantic retrieval path (`text-embedding-3-small`) still ranks the YAML front matter ahead of the prose because each chunk begins with `---`, and the snippet presented to the ranking model contains little beyond metadata.
- Four of the six audit queries (host network driver, rootless, content trust, notification policy) deliver only metadata-heavy chunks within the top 10 positions; the useful paragraphs are available in the document but never surface because the metadata block is identified as `FRONT_MATTER` / `noise`.
- The remaining queries either rank good chunks first (`Quando usar módulos`) or have useful prose that follows shortly after the front matter (`workspace`), so they are less impacted.

## Query health

| Query | Top chunk | Useful chunk in top results? | Notes |
| --- | --- | --- | --- |
| *O que é um workspace no Terraform?* | `FRONT_MATTER` (score 0.643, signals: front_matter / page_title / description / generated_metadata) | Yes (`TRECHO_UTIL_USO` at score 0.633) | The useful content exists immediately after the metadata, but the front matter still beats it. |
| *Quando usar módulos no Terraform?* | `TRECHO_UTIL_USO` (score 0.650) | Yes (rank 1) | Ranking is already healthy. |
| *O que é o host network driver no Docker?* | `FRONT_MATTER` (score 0.655, signals: front_matter / description / keywords / aliases) | No | Top 10 chunks are all metadata; the explanatory paragraph (which sits after the metadata inside the same chunk) never reaches the top. |
| *Para que serve o modo rootless no Docker?* | `FRONT_MATTER` (score 0.612) | Yes, but down at rank 8 with score 0.381 (`TRECHO_UTIL_COMPARACAO`) | Metadata suppresses even unrelated explanatory text about multi-platform builds. |
| *O que é content trust no Docker?* | `FRONT_MATTER` (score 0.691, signals: front_matter / description / keywords / aliases) | Yes, but only after multiple alias chunks (first useful chunk has score 0.425) | The useful paragraphs are present but trapped behind the metadata. |
| *O que é uma notification policy no Grafana Alerting?* | `FRONT_MATTER` (score 0.701, signals: description / keywords / aliases / docs_path / notification_path) | Yes, but only rank 3 (`MISTO`, score 0.673) | Alias-heavy redirects and canonical URLs dominate the retrieval view. |

## Root cause
- The chunking logic preserves the front matter block (titles, descriptions, aliases, keywords) at the beginning of every chunk. Because the snippet provided to the ranking model is limited to the first ~180 characters, those metadata blocks score higher even when the rest of the chunk is the answer.
- The structural_noise penalties flag these chunks as `front_matter`, `description`, etc., but the penalty (max 0.6) is insufficient to counteract the lexical signal, so metadata chunks still outrank the proper paragraphs.

## Recommended next step (to be handled in the next iteration)
- Trim or skip the YAML front matter before chunking so that the chunk starts with narrative text, or explicitly create chunks that separate metadata from body text and discard the metadata-only chunks from the search index.
