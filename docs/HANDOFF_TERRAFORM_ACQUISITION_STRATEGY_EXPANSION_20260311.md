# Handoff: ampliacao da estrategia de aquisicao documental (Terraform)

Data: 2026-03-11
Escopo: atualizacao documental (sem mudanca funcional de pipeline)

## Resumo curto
- A estrategia foi ampliada para **mesclar, nao substituir**.
- Aquisicao via **HTML oficial espelhado** continua valida.
- Aquisicao via **repositorio oficial clonado** passa a ser opcao complementar para Terraform e casos semelhantes.
- A escolha da origem passa a considerar qualidade da fonte e estrutura do conteudo.

## Regras praticas consolidadas
- Usar repo oficial quando a documentacao-fonte estiver mais limpa/estruturada para ingestao.
- Usar HTML espelhado quando for mais simples operacionalmente ou mais fiel ao conteudo publicado.
- Permitir coexistencia das duas abordagens no acervo.
- Manter controle de redundancia/deduplicacao por conteudo e origem antes de promocao final.

## O que nao mudou
- Nenhuma abordagem anterior foi removida.
- Nenhuma logica do pipeline foi alterada.
- Nenhuma etapa nova foi aberta.
