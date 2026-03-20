# Knowledge Router Test Plan

## Context
The knowledge router now depends on `app/knowledge/knowledge_front_registry.json` to know which domains are eligible for semantic routing. Every front that completed `closure_decision` must have an entry, and the router should only turn on routing when semantic embeddings, the semantic baseline, and the closure decision are all confirmed. This plan enumerates how to exercise each registered domain.

## Execution checklist
1. **Registry verification:** open `app/knowledge/knowledge_front_registry.json` and confirm each closed front (Java, OpenAI Products, Terraform, Docker, Kubernetes, Python, PostgreSQL, Linux and the C pilot) is listed with `status: "closed"`, a valid `index_path`, and `enabled_for_routing` reflecting whether the domain is routeable.
2. **Evidence crawl:** for each entry, ensure the referenced `final_report` and `handoff` artifacts exist to satisfy the closure rules before enabling routing.
3. **Routing queries:** send the representative queries below through the router (or the routing evaluation harness) and observe that the returned semantic candidate points to the expected front and index.
4. **Disabled pilot check:** verify that the `C_PILOT` entry remains in the registry for traceability but with `enabled_for_routing: false`, and confirm the router does not surface that domain when the pilot query runs.
5. **Post-check updates:** if any query misroutes or a field drifts (e.g., `enabled_for_routing` flips before embeddings/semantic baseline are ready), correct the registry, rerun the query suite, and record the regression in the status log.

## Representative queries
| Domain | Representative query | Expected router front | Notes |
| --- | --- | --- | --- |
| JAVA | `How do I chain Stream.map, filter and collect to accumulate results?` | `JAVA` | Use the Java pilot index and verify the router returns the Java chunks used in the 18-query semantic baseline. |
| OPENAI_PRODUCTS | `How can I stream ChatCompletions responses on the new OpenAI Realtime API?` | `OPENAI_PRODUCTS` | Ensure the router hits the OpenAI products index rather than routing to general platform docs. |
| TERRAFORM | `What is the difference between terraform plan and terraform apply, and when do I use workspaces?` | `TERRAFORM` | Expect routing to the terraform pilot sandbox after the semantic refinement. |
| DOCKER | `What does a multi-stage Dockerfile look like for a Go binary?` | `DOCKER` | Confirm the router surfaces the Docker runtime index and not similar container questions from other domains. |
| KUBERNETES | `When should I use a StatefulSet instead of a Deployment in Kubernetes?` | `KUBERNETES` | The response should cite the Kubernetes pilot chunks covering pods/services/statefulsets. |
| PYTHON | `When should I use asyncio.run instead of manually driving the event loop?` | `PYTHON` | Validate the router prefers the Python index with the async/stdlib guidance. |
| POSTGRESQL | `How should I index a JSONB column for fast querying in PostgreSQL?` | `POSTGRESQL` | Expect PostgreSQL front to dominate the ranking with JSONB/indexing content. |
| LINUX | `Which systemd unit type handles a oneshot command, and how is it configured?` | `LINUX` | Ensure the Linux front is returned (notice the emphasis on systemd units). |
| C_PILOT | `What does the assert macro do when the condition fails in C?` | *No globally routable front* | The router should *not* resolve to the C pilot because `enabled_for_routing` is false; if it does, treat the incident as a regression. |

## Regression guardrails
- Re-run this plan whenever a new front reaches `closure_decision`, adding its sample queries and verifying the registry update before enabling routing.
- Document each execution of this plan in `STATUS.md`, referencing the commands or harness used and flagging any divergence (e.g., missing registry entry, misrouting) for follow-up.
