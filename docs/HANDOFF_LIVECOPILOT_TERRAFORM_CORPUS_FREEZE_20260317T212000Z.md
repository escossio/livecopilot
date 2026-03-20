# Handoff LiveCopilot Terraform Corpus Freeze (2026-03-17T21:20:00Z)

## Contexto
- Etapa 2 do Terraform (manifesto) concluiu a lista e os lotes; agora iniciamos Etapa 3 (congelamento).  
- O objetivo é baixar apenas o Lote 1 (linguagem, CLI, state/backends/workspaces) sem avançar para parsing.

## Ações realizadas
1. criamos a estrutura `data/knowledge_raw/terraform/{cli,language,state,backends,workspaces,metadata}` para armazenar o corpus bruto.  
2. baixamos as páginas oficiais do CLI, da linguagem e dos backends (cada uma em seu subdiretório) usando `curl -L`, garantindo foco apenas no Lote 1.  
3. calculamos hashes SHA-256 e registramos o snapshot em `data/knowledge_raw/terraform/metadata/snapshot.md`.  
4. registramos o congelamento no lockfile (`docs/TERRAFORM_CORPUS_LOCK.md` e `.json`), destacando fontes incluídas, fontes adiadas e observações (hash, formato).  

## Estado final do corpus
- Lote 1 congelado com os HTMLs das principais páginas; cada artefato tem hash e caminho.  
- O lockfile menciona as fontes não congeladas (modules, providers, materiais secundários) e o motivo da postergação.  
- O manifesto mantém rastreio completo da política + dos lotes iniciados.

## Próximos passos sugeridos
1. validar os hashes e liberar o Lote 1 para parsing/chunking.  
2. após parsing, planejar a bateria de perguntas Terraform alinhada ao escopo do Lote 1.  
3. manter o lockfile atualizado conforme novos lotes forem congelados.
