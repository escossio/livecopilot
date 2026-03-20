# Domain Specification Schema

Cada domínio usa um arquivo YAML com os campos:

- `name`: identificador curto
- `description`: resumo do escopo
- `current_stage`: etapa atual do pipeline
- `raw_sources`: lista de URLs ou referências brutas
- `parsed_sources`: referências parseadas aprovadas
- `chunk_paths`: caminhos para chunks gerados
- `validation_sets`: conjuntos usados na validação
- `notes`: observações operacionais
