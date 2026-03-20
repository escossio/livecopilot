# Terraform Source Manifest — 2026-03-17T21:00:00Z

## Contexto
- partimos da política official-first registrada em `docs/TERRAFORM_OFFICIAL_SOURCE_POLICY.md` e dos pilotos C/Python documentados (`docs/C_PILOT_FINAL_REPORT.md`, `docs/PYTHON_DOMAIN_FINAL_REPORT.md`).
- este manifesto executa a Etapa 2: transforma escopo e priorização em fontes concretas, lotes e estratégias antes de congelar qualquer coisa.

## Fontes confirmadas
| Fonte | Categoria | Tipo | URL principal | Espelho | Disponibilidade | Observações/licença | Estratégia de coleta | Prioridade | Lote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Terraform CLI docs | PRIMARIA | HTML/CLI | https://www.terraform.io/docs/cli/index.html | https://developer.hashicorp.com/terraform/cli | pública | licença Apache 2.0 (HashiCorp) | baixar páginas principais do CLI, manter versão do release usado | alta | 1 |
| Terraform language docs | PRIMARIA | HTML/LANGUAGE | https://www.terraform.io/docs/language/index.html | https://developer.hashicorp.com/terraform/language | pública | oficial HashiCorp | capturar capítulos de HCL, expressions, variables, outputs e modules | alta | 1 |
| Terraform state/backends/workspaces docs | PRIMARIA | HTML/STATE | https://www.terraform.io/docs/backends/index.html | https://developer.hashicorp.com/terraform/backends | pública | oficial HashiCorp | baixar seções de backends (S3, GCS, Terraform Cloud) + workspaces | alta | 1 |
| Terraform modules documentation | PRIMARIA | HTML/MODULES | https://www.terraform.io/docs/language/modules/index.html | https://developer.hashicorp.com/terraform/language/modules | pública | oficial HashiCorp | capturar imediato e passes de registry module best practices | alta | 2 |
| Terraform Registry provider AWS | PRIMARIA | REGISTRY | https://registry.terraform.io/providers/hashicorp/aws/latest/docs | n/a | pública | Apache 2.0 | baixar páginas de recursos (EC2, iam, s3, etc) que atendem ao subset inicial, mapear dependências | média | 3 |
| Terraform Registry provider Azure | PRIMARIA | REGISTRY | https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs | n/a | pública | Apache 2.0 | priorizar resources Azure App Service, network, storage | média | 3 |
| Terraform Registry provider Google | PRIMARIA | REGISTRY | https://registry.terraform.io/providers/hashicorp/google/latest/docs | n/a | pública | Apache 2.0 | priorizar resources compute, storage, IAM | média | 3 |
| HashiCorp Learn Terraform tutorials | SECUNDARIA | GUIDE | https://developer.hashicorp.com/terraform/tutorials | n/a | pública | oficial | extrair tutorials alinhados ao recorte (CLI/language/state/modules) e registrar sequência | baixa (após lote 3) | 4 |
| Terraform release notes (CLI & Providers) | SECUNDARIA | DOC | https://www.terraform.io/docs/release/index.html | n/a | pública | oficial | coletar notes relevantes quando impactam CLI ou providers prioritários | baixa | 4 |
| Terraform Cloud authentication guide | SECUNDARIA | GUIDE | https://developer.hashicorp.com/terraform/cloud | n/a | pública | oficial HashiCorp | capturar apenas capítulos de backend/workspace authentication | baixa | 2 |
| Blogs, Medium, StackOverflow, repos de terceiros | NAO_PRIORIZAR_AGORA | OTHER | n/a | n/a | n/a | não aplicar | n/a | n/a |

## Estratégia de lotes
1. **Lote 1 (linguagem + CLI + state/backends/workspaces)**: documenta comandos, HCL e modelos de estado para responder perguntas básicas sobre plan/apply, variables, outputs e backends.  
2. **Lote 2 (modules + Terraform Cloud / authentication)**: captura módulos oficiais, composição e guias de Terraform Cloud que suportam modules/registries e workspaces.  
3. **Lote 3 (providers iniciais)**: ingere os resources mais utilizados do AWS, Azure e Google para dar cobertura a cenários práticos comuns do LiveCopilot.  
4. **Lote 4 (materiais secundários oficiais)**: integra HashiCorp Learn e release notes apenas depois que o core estiver consolidado para evitar ruído.

## Justificativas e riscos
- As fontes do Lote 1 entram primeiro porque sustentam o entendimento da linguagem, CLI e estado, que permitem responder perguntas críticas sem a complexidade dos providers.  
- Os providers ficam para o Lote 3 porque demandam volume de páginas e precisam do contexto da linguagem/plan/state para serem úteis; até lá o core já explicará as abstrações.  
- O HashiCorp Learn e os changelogs são mantidos para o final (Lote 4) para servir de material de reforço sem distrações iniciais.  
- Riscos: o Registry muda frequentemente (nova versão de provider), exigindo controle de versão; a sobreposição entre docs oficiais e Learn pode gerar conteúdo duplicado; providers geram muito volume, então limitamos o subset às families definidas.

## Próximos passos indicados
1. congelar os lotes seguindo a ordem proposta assim que forem aprovados.  
2. garantir que cada lote tenha a URL, hash e metadados antes de avançar para parsing.  
3. elaborar bateria de perguntas iniciais para o recorte Terraform antes do chunking.
