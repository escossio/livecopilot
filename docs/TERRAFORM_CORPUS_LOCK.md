# Terraform Corpus Lock — 2026-03-18T06:04:26Z

## Escopo congelado (Lote 1)
| Fonte | Status | Observações |
| --- | --- | --- |
| Terraform CLI docs (https://www.terraform.io/docs/cli/index.html) | congelada | salvo em `data/knowledge_raw/terraform/cli/terraform-cli-index.html`, hash listado em `data/knowledge_raw/terraform/metadata/snapshot.md` |
| Terraform language docs (https://www.terraform.io/docs/language/index.html) | congelada | salvo em `data/knowledge_raw/terraform/language/terraform-language-index.html` |
| Terraform state/backends/workspaces docs (https://www.terraform.io/docs/backends/index.html) | congelada | cobre backends e workspaces em um único HTML (`data/knowledge_raw/terraform/state/terraform-backends-index.html`) |
| Terraform modules docs (https://www.terraform.io/docs/language/modules/index.html) | congelada | salvo em `data/knowledge_raw/terraform/modules/terraform-modules-index.html`, hash 72a44e9e... |
| Terraform AWS provider overview (https://registry.terraform.io/providers/hashicorp/aws/latest/docs) | congelada | salvo em `data/knowledge_raw/terraform/providers/aws/aws-overview.html`, hash e2971d5dfc52fe082eff60e34afada113a3795ddf305e1a25658dc99725766e8 |
| AWS Instance resource (https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) | congelada | salvo em `data/knowledge_raw/terraform/providers/aws/aws-instance.html`, hash 9bc18ff26011d27c4c87a78f546e3b100e4d2b91c7f08e0cac7faea9e014225d |

## Fontes não congeladas neste ciclo
| Fonte | Razão |
| --- | --- |
| Terraform modules docs | congelada no Lote 2 (Modules) | procedendo com parsing/chunking neste ciclo |
| Terraform AWS provider overview | congelada no Lote 3 (Providers AWS) | concluindo freeze limitado à overview + aws_instance |
| AWS Instance resource | congelada no Lote 3 (Providers AWS) | partes adicionais aguardam validação lexical |
| Providers AWS/Azure/Google registry | aguardando Lote 3 (demanda volume e depende do contexto de linguagem/plan). |
| HashiCorp Learn tutorials | Lote 4 (material secundário). |
| Release notes / Terraform Cloud guides | Lote 4 / 2 respectivamente. |

## Metadados
- data/knowledge_raw/terraform/metadata/snapshot.md registra hash, formato e caminhos.  
- Cada artefato tem pelo menos um hash SHA-256 calculado.  
- A coleta foi feita via `curl -L` diretamente dos URLs oficiais e dos fontes gerados via `website/docs` do provedor HashiCorp; nenhum mirror alternativo foi necessário.

## Próximos passos
1. liberar a documentação do Lote 1 para parsing/chunking.  
2. preservar os hashes e os diretórios quando for consolidar o subset.  
3. iniciar Lote 2 depois que manifestos e baterias forem aprovados.
