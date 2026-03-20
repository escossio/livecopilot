# Política de Chunking — Domínio Python (2026-03-17T05:30:00Z)

## Objetivo
- formalizar a camada piloto de chunking do Lote 1, mantendo o pipeline official-first e garantindo que cada chunk represente uma unidade semântica útil para perguntas do LiveCopilot.
- limitar o subset inicial a tutorial, language reference, built-ins/exceptions e quatro módulos, documentando os critérios usados antes de qualquer embedding.

## Regras gerais
1. partir do corpus parseado (`data/knowledge_parsed/python/`) e manter a mesma hierarquia de famílias (tutorial, language reference, built-ins/exceptions, modules).
2. chunk por título/seção (`h1`, `h2`, `h3`) para preservar tópicos completos; cada heading gera um chunk que inclui texto até o próximo heading.
3. evitar chunks vazios ou extremamente curtos (mínimo de ~80 tokens) e evitar agrupar headings diferentes em um mesmo chunk.
4. limitar o tamanho do subset piloto a um único arquivo por família e a quatro módulos (pathlib, subprocess, json, argparse) nesta rodada inicial.
5. registrar metadados por chunk (`source_family`, `source_file`, `chunk_id`, `title`, `section`, `length`, `local_path`) para facilitar auditoria e automação.
6. não gerar nenhum embedding ou persistir vetores nesta etapa; o chunking serve apenas como prévia técnica controlada.

## Observações
- O inventário de chunks fica em `docs/PYTHON_CHUNKING_METADATA.json` e pode ser usado para refrescar o subset em rodadas futuras.
- Amostras auditáveis estão no relatório `docs/PYTHON_CHUNKING_SAMPLE_REPORT_20260317T053000Z.md` e demonstram o critério aplicado para cada família.
