# Terraform official-source policy — 2026-03-17T20:00:00Z

## Contexto
- replicamos a disciplina official-first testada nos pilotos C e Python (ver `docs/C_PILOT_FINAL_REPORT.md` e `docs/PYTHON_DOMAIN_FINAL_REPORT.md`) e queremos manter o índice global intocado.
- este documento registra o recorte inicial do domínio Terraform, as fontes candidatas e a priorização oficial-first antes de iniciar qualquer freeze.

## Objetivo do domínio Terraform
- construir um subset útil de infraestrutura como código que responda a perguntas práticas do LiveCopilot sobre configuração de Terraform, mantendo o pipeline isolado até que tenhamos confiança nos chunks e embeddings.
- avaliar a documentação oficial da HashiCorp/terraform.io, mapear os tópicos essenciais do CLI e do idioma e documentar o que entra/agora e o que fica fora.

## Recorte inicial do piloto
Focaremos nos pilares que lidam diretamente com infraestrutura como código e operações básicas do Terraform, evitando o esforço de ingerir toda a plataforma até o piloto ganhar estabilidade:
1. Conceitos básicos (infra-code, fluxo) e nomenclatura oficial.
2. Linguagem de configuração: resources, variables, outputs, providers e modules.
3. Comandos centrais do CLI: `plan`, `apply`, `destroy`, `console`, `fmt` (introdução).  
4. Estado remoto/local, backends (S3, GCS, Terraform Cloud) e workspaces.  
5. Module development/usage (structure, composition, registries).  
6. Providers e resources mais usados (AWS, Azure, Google Compute) dentro do escopo declarado — manter a cobertura manual de recursos conforme for necessário para o subset inicial.

### Por que esse recorte?
- Permite responder perguntas críticas sobre criação/atualização de infra sem ter que cobrir todo o ecossistema (providers, provisioning, integrações avançadas).
- Equipara-se aos pilares testados em C/Python: definimos um subset compacto, documentamos cada etapa e depois expandimos iterativamente.
- Evita diluir a equipe em centenas de modules/recursos antes de validar a rastreabilidade e a qualidade semântica.

## Fontes candidatas
A prioridade é total para materiais oficiais da HashiCorp/terraform.io. Consideramos a classificação oficial-first em C/Python como guia.

### FONTE_PRIMARIA (prioridade máxima)
- `Terraform CLI documentation` (`https://www.terraform.io/docs/cli/index.html`) — cobre comandos (`plan`, `apply`, `state`, `workspace`, `providers`).  
- `Terraform language documentation` (`https://www.terraform.io/docs/language/index.html`) — explica HCL, ciclo de vida do recurso, variables, outputs, expressions e modules.  
- `Terraform Registry reference docs` e guias oficiais dos providers selecionados (AWS, Azure, Google) que atendem ao recorte inicial de providers/resources (por exemplo, `https://registry.terraform.io/providers/hashicorp/aws/latest/docs`).  
- `Terraform state, backends e workspaces` (seções oficiais dedicadas no site HashiCorp) para entender persistência, locking e estratégias recomendadas.  
- Documentação oficial de módulos e práticas recomendadas (`https://www.terraform.io/docs/language/modules/index.html`).

### FONTE_SECUNDARIA (relay oficial / complementos aprovados)
- `HashiCorp Learn tutorials específicos` (`https://developer.hashicorp.com/terraform/tutorials`) pequenos módulos oficiais com hands-on que reforçam os conceitos do recorte.  
- `Release notes e changelogs` (HashiCorp CLI/Provider release notes) somente quando vinculados aos tópicos do recorte.  
- `Guia oficial de authentication/integration com Terraform Cloud` dado que impacta backends e workspaces, mas apenas depois de validar o core CLI/linguagem.

### NAO_PRIORIZAR_AGORA (fora do piloto)
- Blogs, Medium, posts aleatórios, StackOverflow e cursos não oficiais (mesmo que mencionem Terraform).  
- Repositórios de terceiros, exemplos GitHub (exceto os módulos oficiais publicados no Registry).  
- Qualquer conteúdo que não venha diretamente de terraform.io, hashicorp.com ou registries certificados.

## O que entra agora
- Base oficial do Terraform CLI e linguagem (HCL), com foco em plan/apply/state/workspace/modules.  
- Providers e resources essenciais citados na documentação oficial; priorizar AWS, Azure e Google para cobrir casos de uso comuns do LiveCopilot.  
- Estado e backends documentados pela HashiCorp (S3, Terraform Cloud, etc.).  
- Módulos oficiais com boas práticas de composition/reuse.

## O que fica de fora até o próximo ciclo
- Blogs de terceiros, StackOverflow, cursos e materiais pagos.  
- Artigos ou módulos comunitários não aprovados pela HashiCorp.  
- Infraestrutura de provisioning além do CLI (ex: Partner offerings, pipelines CI/CD) salvo decisão futura bem documentada.

## Riscos e limitações
- O recorte inicial não cobre todas as providers nem tópicos avançados (ex: networking avançado, telecom).  
- Há dependência do Terraform Registry para garantir que os providers escolhidos mantenham referências estáveis.  
- Como ainda não congelamos o corpus, o pipeline manterá supervisão próxima antes de prosseguir para parsing/chunking.

## Próximos passos sugeridos
1. Produzir manifesto operacional de fontes com URLs, lotes e hashes (Etapa 1 futura).  
2. Congelar subset oficial (Etapa 2) apenas após aprovação do manifesto.  
3. Garantir que o escopo está alinhado com perguntas iniciais definidas em roteiro semelhante à bateria C/Python.
