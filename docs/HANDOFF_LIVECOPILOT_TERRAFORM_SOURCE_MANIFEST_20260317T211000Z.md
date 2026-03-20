# Handoff LiveCopilot Terraform Source Manifest (2026-03-17T21:10:00Z)

## Contexto
- o domínio Terraform já tem recorte e política oficial-first documentados em `docs/TERRAFORM_OFFICIAL_SOURCE_POLICY.md`.
- esta etapa cria o manifesto executável com lotes, prioridades e estratégias de coleta (Etapa 2) antes de iniciar qualquer freeze.

## Ações realizadas
1. definimos a lista concreta de fontes (CLI, linguagem, state/backends, modules, providers AWS/Azure/Google, Learn, release notes, Terraform Cloud) com categoria, tipo, URLs, observações e prioridade conforme exigido pela instrução.  
2. estruturamos os lotes operacionais (Lote 1: linguagem/CLI/state, Lote 2: modules/Terraform Cloud, Lote 3: providers, Lote 4: materiais secundários oficiais) e justificamos por que essa ordem protege o subset inicial.  
3. geramos o manifesto `docs/TERRAFORM_SOURCE_MANIFEST.md` com tabelas e explicações e um artefato JSON (`docs/TERRAFORM_SOURCE_MANIFEST.json`) para uso futuro por scripts.

## Estado final
- manifesto operacional pronto, com fontes confirmadas e estratégias de coleta por lote.  
- lotes definidos e priorizados prontos para serem congelados assim que o manifesto for aprovado.  
- o domínio permanece documentado mas ainda sem ingestão, mantendo o índice global intacto.

## Próximos passos sugeridos
1. congelar o Lote 1 (linguagem/CLI/state) e registrar hashes/URLs.  
2. gerar bateria de perguntas iniciais similar às usadas em C/Python antes de chunking.  
3. depois do freeze da base oficial, avançar no Lote 2 (modules) e assim por diante, acompanhando o manifesto.
