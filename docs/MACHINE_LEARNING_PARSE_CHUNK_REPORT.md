# MACHINE LEARNING — Parse/Chunk Report

## Document count
- 4 documentos HTML oficiais (as páginas autorizadas listadas no manifesto).

## Parsed documents
- 4 (cada HTML gerou parsing válido com status `parsed`).

## Chunks
- Chunk total gerado: 8 (2 chunks por documento com `chunk_size` 1200 e `overlap` 180).
- Chunk size médio objetivo: 1200 caracteres (o pipeline manteve o parâmetro padrão). 

## Arquivos processados
- `machine_learning/framework_user_guide/user_guide_html.html`
- `machine_learning/framework_user_guide/user_guide_html.metadata.json`
- `machine_learning/framework_reference/index_html.html`
- `machine_learning/framework_reference/index_html.metadata.json`
- `machine_learning/framework_guide/guide.html`
- `machine_learning/framework_guide/guide.metadata.json`
- `machine_learning/educational_course/crash_course.html`
- `machine_learning/educational_course/crash_course.metadata.json`

## Erros
- Nenhum erro de parsing. As quatro metadatas (`.metadata.json`) foram identificadas como tipos não suportados e ignoradas sem gerar chunks.
