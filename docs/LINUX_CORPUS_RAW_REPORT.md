# Linux Corpus Raw Materialization Report

## Resumo
- `document_count`: 4
- `avg_word_count`: 65.25 palavras por arquivo
- `parsing`: não executado
- `chunking`: não executado
- `embeddings`: não executado

## Arquivos criados
- `data/knowledge_raw/linux/kernel_subsystem.md`
- `data/knowledge_raw/linux/systemd_overview.md`
- `data/knowledge_raw/linux/networking.md`
- `data/knowledge_raw/linux/man_ps.md`

## Fontes efetivamente usadas
- Kernel documentation (`https://www.kernel.org/doc/html/latest/`)
- systemd overview & man pages (`https://www.freedesktop.org/wiki/Software/systemd/`, `https://www.freedesktop.org/software/systemd/man/index.html`)
- Linux networking docs (`https://www.kernel.org/doc/html/latest/networking/`)
- man7 Linux man pages (`https://man7.org/linux/man-pages/dir_section_1.html`)

## Observações
- Cada arquivo preserva seções técnicas (subsystems, units, networking stack, comando `ps`) e elimina navegação/marcas de distribuição.\n+- Documentação voltada para administração e operações, alinhada ao escopo upstream definido anteriormente.
