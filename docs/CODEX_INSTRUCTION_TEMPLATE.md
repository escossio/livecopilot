# Codex Instruction Template

Use este template sempre que for gerar uma instrução operacional ao Codex. Todos os campos são obrigatórios e devem ser preenchidos com detalhes objetivos.

```
MODELO_RECOMENDADO: [mini|max|...]
JUSTIFICATIVA_DO_MODELO: [Por que este modelo atende ao objetivo]
OBJETIVO: [Resultado desejado da rodada]
ESCOPO: [O que está incluído e, se necessário, o que fica fora]
NAO_FAZER: [Lista de ações claras proibidas nesta rodada]
ENTRADAS: [Arquivos, dados ou contexto necessário]
PASSOS: [Etapas enumeradas da execução]
VALIDACAO: [Como a entrega será validada]
ARTEFATOS_ESPERADOS: [Resultados tangíveis esperados]
CRITERIO_DE_PARADA: [Condições que encerram a rodada]
ENTREGA_FINAL: [Forma completa da entrega, mensagens finais ou arquivos]
ARQUIVOS_DE_CONTEXTO: [Arquivos relevantes já revisados ou suplementares]
```

Sempre anexe referências adicionais (logs, checkpoints) na seção `ARQUIVOS_DE_CONTEXTO` para facilitar o rastreio posterior.
