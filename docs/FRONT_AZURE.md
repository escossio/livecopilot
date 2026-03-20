# FRONT AZURE

## Objetivo
- Abrir a frente Azure para governar o ciclo documental oficial (serviços core, compute, redes, storage, identidade e CLI) antes de avançar para parsing e validações.

## Escopo
- Domínio: serviços core do Azure, compute (VMs, App Services), networking (VNET, load balancers), storage (blob, file, data lake), identidade (Azure AD, RBAC) e CLI oficial (`az`).
- Exclusões: conteúdo de terceiros, blogs, vídeos promocionais e implementações específicas de parceiros que não estejam na documentação Microsoft Learn/Azure docs.

## Source policy
- Fontes permitidas: `learn.microsoft.com` (Azure docs, Microsoft Learn) com foco nos tópicos core acima e nas referências oficiais do Azure CLI.
- Conteúdo deve ser técnico, atualizado e rastreável; evitar páginas de marketing, blog posts e artigos de terceiros.
- Priorizar documentação que mencione explicitamente produtos oficiais (VMs, Storage, Networking, Identity) e APIs do Azure.

## Source manifest (inicial)
- Azure Architecture Center (`https://learn.microsoft.com/en-us/azure/architecture/`) – visão geral dos serviços, padrões e boas práticas do Azure core.
- Azure CLI Overview (`https://learn.microsoft.com/en-us/cli/azure/`) – referência oficial da CLI, comandos básicos e extensões.
- Azure Networking documentation (`https://learn.microsoft.com/en-us/azure/networking/`) – VNETs, load balancers, firewall e conectividade.
- Azure Storage documentation (`https://learn.microsoft.com/en-us/azure/storage/`) – blobs, file shares, data lake e camadas de armazenamento.
- Azure Identity (`https://learn.microsoft.com/en-us/azure/active-directory/`) – Azure AD, RBAC, identity governance.

## Corpus lock (inicial)
- Scoped: os URLs listados acima; o corpus será materializado em `data/knowledge_raw/azure/` e congelado até o próximo passo.
- Fora do lock: sites de parceiros, blogs, marketing e conteúdos duplicados sem vínculo direto com a docs oficial.

## Status
- state: `closed`
- stage: `closure_decision`
- fechamento: final report e handoff registrados (`docs/AZURE_FINAL_REPORT_20260319T190000Z.md`, `docs/HANDOFF_LIVECOPILOT_AZURE_FRONT_CLOSURE_20260319T190000Z.md`).
- próximo passo: manter o índice pronto para queries core e reabrir apenas se o scope oficial for expandido.

## Lifecycle oficial
- Pipeline completo documentado em `docs/FRONT_LIFECYCLE_CONTRACT.md`; a frente começa em `corpus_preparation`.

## Observação
- Nenhuma ingestão, parsing, chunking ou embedding foi executado; esta fase registra apenas o escopo e o plano de corpus.
