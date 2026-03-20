# Chunking before / after (front matter) · 2026-03-15T21:12Z

## Terraform · workspace
**Antes (front matter no topo)**  
```text
---
page_title: 'State: Workspaces'
description: >-
Workspaces allow the use of multiple states with a single configuration
directory.
# START AUTO GENERATED METADATA, DO NOT EDIT
```

**Depois (chunk começa no conteúdo útil)**  
```text
# Workspaces

Each Terraform configuration has an associated [backend](/terraform/language/backend) that defines how Terraform executes operations and where Terraform stores persistent data, like [state](/terraform/language/state/purpose).
```

## Grafana Alerting · notification policy
**Antes (frente com aliases/canonical)**  
```text
---
aliases:
- ../notification-policies/notifications/ # /docs/grafana/<GRAFANA_VERSION>/alerting/fundamentals/notification-policies/notifications/
canonical: https://grafana.com/d
```

**Depois (resumo da política no corpo)**  
```text
Notification policies provide you with a flexible way of designing how to handle notifications and minimize alert noise.

Using label matchers, alert instances are [routed to notification policies](#routing). The notification policy can then [group multiple alert instances into a single notification](ref:group-alert-notifications) and deliver it to the contact point.
```
