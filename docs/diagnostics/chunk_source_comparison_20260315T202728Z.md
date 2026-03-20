# Chunk Source Comparison 20260315T202728Z

This note pairs the excerpts that the semantic search ranked highest with the original document regions they cover. Front-matter chunks (with `---`) are clearly identifiable in the returned snippets and are contrasted with the downstream prose that actually answers the question.

## O que é um workspace no Terraform?

**Rank 1 (front matter, `chunk_type=noise`, similarity 0.643)**  

```
---
page_title: 'State: Workspaces'
description: >-
Workspaces allow the use of multiple states with a single configuration directory.
# START AUTO GENERATED METADATA, DO NOT EDIT
created_at: 2025-11-19T13:27:46Z
last_modified: 2025-11-19T13:27:46Z
# END AUTO GENERATED METADATA
---

# Workspaces
Each Terraform configuration has an associated backend that defines how Terraform executes operations and where Terraform stores persistent data, like state.
```

The parser sees the same block at the top of the source document (`# Workspaces` followed immediately by the metadata), so the search result only returns the metadata even though the chunk also contains the useful definition that follows.

**First useful chunk (`TRECHO_UTIL_USO`, similarity 0.633)**  

```
Terraform starts with a single, default workspace named `default` that you cannot delete. If you have not created a new workspace, you are using the default workspace in your Terraform working directory.

When you run `terraform plan` in a new workspace, Terraform does not access existing resources in other workspaces. These resources still physically exist, but you must switch workspaces to manage them.
```

This chunk exists immediately after the metadata in the same document and therefore can answer the question, but its score is ~0.63 versus the front matter’s 0.64 because the ranking sees the metadata first.

## Quando usar módulos no Terraform?

**Rank 1 (`TRECHO_UTIL_USO`, similarity 0.65)**  

```
## When to write a module

In principle any combination of resources and other constructs can be factored out into a module, but over-using modules can make your overall Terraform configuration harder to understand and maintain, so we recommend moderation.
```

This query already retrieves substantive text first, which is why the response was previously marked as coherent.

**Rank 2 (`TRECHO_UTIL_MECANISMO`, similarity 0.627)** – the follow-up chunk describes module structure and continues the explanation.

## O que é o host network driver no Docker?

**Rank 1 (front matter, `chunk_type=noise`, similarity 0.655)**  

```
---
title: Host network driver
description: All about exposing containers on the Docker host's network
keywords: network, host, standalone, host mode networking
aliases:
- /network/host/
- /network/drivers/host/
- /engine/network/tutorials/host/
---

If you use the `host` network mode for a container, that container's network stack isn't isolated from the Docker host...
```

The chunk contains the explanation, but because it begins with the metadata block and _the snippet sent to the ranker stops inside that block_, the metadata dominates the score (structural noise reasons are `front_matter`, `description`, `keywords`, `aliases`). None of the top 10 results expose the paragraph that starts “If you use the `host` network mode…”.

## Para que serve o modo rootless no Docker?

**Rank 1 (front matter, `chunk_type=noise`, 0.612)**  

```
---
description: Run the Docker daemon as a non-root user (Rootless mode)
keywords: security, namespaces, rootless
title: Rootless mode
weight: 10
---

Rootless mode lets you run the Docker daemon and containers as a non-root user to mitigate potential vulnerabilities in the daemon and the container runtime.
```

Again, the metadata is the first text seen by the ranker. The first chunk that is not tagged as noise is rank 8, a generic “Docker solves the ‘it works on my machine’ problem” paragraph (similarity 0.381) that does not mention rootless mode, because no higher-scoring chunk made it past the metadata threshold.

## O que é content trust no Docker?

**Rank 1 (front matter, `chunk_type=noise`, 0.691)**  

```
---
description: Enabling content trust in Docker
keywords: content, trust, security, docker, documentation
title: Content trust in Docker
aliases:
- /engine/security/trust/content_trust/
---

When transferring data among networked systems, trust is a central concern...
```

The chunk contains the actual introduction, but it is returned as part of a metadata-heavy snippet (`front_matter`, `description`, `keywords`, `aliases`). That is why the question persists even though the document has a precise section on Docker content trust.

## O que é uma notification policy no Grafana Alerting?

**Rank 1 (front matter, `chunk_type=noise`, 0.701)**  

```
---
aliases:
- ../notification-policies/notifications/
canonical: https://grafana.com/docs/...
description: Learn about how notification policies work and are structured
keywords:
- grafana
- alerting
title: Notification policies
weight: 113
refs:
shared-alert-labels:
- pattern: /docs/grafana/
  destination: /docs/grafana/<GRAFANA_VERSION>/alerting/...
---
```

The top metadata chunk is mostly alias redirection, so the snippet gives no definition. Only after these redirect fragments does any actual content appear (rank 3 is a short “click Alerts & IRM → Alerting → Notification policies” snippet with classification `MISTO`).

This comparison confirms that the ingestion preserves the YAML block (aliases, canonical URLs, keywords) at the very top of each chunk, and those blocks consistently win the retrieval race for the remaining problematic queries.
