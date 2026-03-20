# Relatório de chunking — Python Lote 1 (2026-03-17T05:30:00Z)

## Amostras
| Amostra | Fonte | Chunk ID | Critério de corte | Avaliação |
| --- | --- | --- | --- | --- |
| builtins_exceptions | builtins_functions | builtins_functions-1 | heading `Built-in Functions ¶` | snippet: Built-in Functions ¶ The Python interpreter has a number of functions and types built into it that are always available.  They are listed here in alphabetical o... |
| language_reference | language_reference | language_reference-1 | heading `The Python Language Reference ¶` | snippet: The Python Language Reference ¶ This reference manual describes the syntax and “core semantics” of the language. It is terse, but attempts to be exact and compl... |
| modules | argparse | argparse-1 | heading `argparse — Parser for command-line options, arguments and subcommands ¶` | snippet: argparse — Parser for command-line options, arguments and subcommands ¶ Added in version 3.2. Source code: Lib/argparse.py Note While argparse is the default re... |
| tutorial | tutorial | tutorial-1 | heading `The Python Tutorial ¶` | snippet: The Python Tutorial ¶ Tip This tutorial is designed for programmers that are new to the Python language, not beginners who are new to programming. Python is an ... |

## Observações
- O subset piloto incluiu uma página de tutorial, uma de language reference, o built-in functions e um módulo (o primeiro do lote) para validar o chunking sem gerar todos os chunks.
- Cada chunk preserva título, seção e pelo menos 80 tokens para manter contexto, evitando fragmentos minúsculos.
- Metadados estão em `docs/PYTHON_CHUNKING_METADATA.json` e podem alimentar scripts de chunking local.
