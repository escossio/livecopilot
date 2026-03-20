# Chunk Quality Audit 20260315T202728Z

## Methodology
- Queries executed against the live `semantic/search` endpoint (limit 10, `text-embedding-3-small`), preserving the actual production retrieval path.
- Each chunk is annotated with `_classify_chunk_semantic_type`, `_structural_noise_penalty` and a lightweight comparison against the downstream parsed document so we can see whether the front matter metadata is outranking the substantive paragraphs.
- The resulting JSON `chunk_quality_audit_20260315T202728Z.json` contains every score used below.

## Findings

### O que é um workspace no Terraform?
- Rank 1 is the metadata chunk that starts with `---` (front_matter, page_title, description, generated_metadata), so the similarity score (0.643) is driven by the YAML block before the actual content even begins.
- Rank 2 (`TRECHO_UTIL_USO`, score 0.633) is the paragraph that explains Terraform workspaces and how the backend partitions persistent state. It exists in the corpus but is penalized by having to compete with the front-matter chunk that shares the same first 200 characters.
- Conclusion: the useful chunk exists, but it is pushed down the ranking as long as the ingestion preserves front matter blocks as their own chunks (or as the leading portion of a chunk with `chunk_type=noise`).

### Quando usar módulos no Terraform?
- Rank 1 is already a `TRECHO_UTIL_USO` chunk; both the `When to write a module` heading and the following “factor out resources” paragraph lead the ranking with a full-text similarity of 0.650.
- Structural signals are clean, so this query is not suffering from the metadata problem.

### O que é o host network driver no Docker?
- Top ten results are all `FRONT_MATTER`/`noise` chunks whose snippets stop at the YAML header `title / description / keywords / aliases`.
- No useful chunk was emitted inside the first 10 hits, even though `docker_docs_selected/.../host.md` contains the explanation (“If you use the `host` network mode...”). Because the chunk starts with front matter, the lexical similarity is dominated by the metadata and the chunk_type stays `noise`, so there is no chance for the definition to rise.
- Root cause: chunking/ingestion retains the front matter block at the beginning of the chunk, allowing the metadata-heavy snippet to win before the real sentence does.

### Para que serve o modo rootless no Docker?
- Rank 1 is front matter (`description`, `keywords`, `aliases`).
- The first chunk flagged as useful is rank 8 (`TRECHO_UTIL_COMPARACAO`, similarity 0.381), so the response must rely on low-scoring content after many metadata-heavy hits.
- Same ingestion pattern as above: the chunk begins with front matter, so the metadata snippet outranks the descriptive paragraph by a wide margin.

### O que é content trust no Docker?
- Ranks 1‑6 are front matter/aliases (`content trust`, `play in trust sandbox`, `manage keys`).
- The first non-noise classification (rank 7) is `MISTO` (similarity 0.425), and the useful “Chapter Summary” text does not surface until after all metadata blocks.
- Metadata-heavy aliases and descriptions are registering as `structural_noise_reasons` (`front_matter`, `description`, `keywords`, `aliases`), yet the current pipeline still exposes them because they appear before the useful content.

### O que é uma notification policy no Grafana Alerting?
- The first two hits are alias-heavy `FRONT_MATTER` blocks (`aliases: - ../notification-policies/...`).
- Additional metadata chunks (gateway redirects, `notification_path`) occupy ranks 3‑10; only the navigation steps (rank 3, `MISTO`) show actionable text, but even that score (0.673) is lower than the front matter snippets.
- The relevant definition exists deeper in the doc, yet the surrounding YAML/alias definitions keep being promoted.

## Summary
- Four of the six target queries (host network driver, rootless, content trust, notification policy) are completely dominated by front matter/metadocumentation chunks, so the retrieved context never exposes the actual definition.
- The remaining queries (workspace, modules) do have useful chunks, but the workspace definition only surfaces after the metadata is demoted, and the ranking still has to work around the same pattern.
- The structural noise penalties are not strong enough when the chunk collects metadata and body text as a single unit; every problematic chunk still triggers `front_matter` and related signals, yet it is treated as the best match because the metadata lives at the top of the chunk.
