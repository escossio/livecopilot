# Linux Corpus Preparation

## Estratégia de ingestão
- Capturar a documentação upstream do kernel (`kernel.org`), systemd/freedesktop (`freedesktop.org`) e páginas man oficiais (`man7.org`), priorizando versão estável mais recente.
- Utilizar pipelines de download controlado com hashes e registrar datas de captura.
- Converter cada documento para markdown, mantendo seções técnicas e exemplos operacionais (systemd units, comandos de rede, fs).

## Tipos de conteúdo permitidos
- kernel subsystem documentation, network stacks, filesystems, security guides e systemd unit/service definitions.
- Páginas man7 para comandos essenciais (`ps`, `ip`, `journalctl`, `systemctl`, `mount`, `umask`), mantendo seções de sintaxe e flags.
- Documentos de sysadmin com foco em operations (process management, journald, networking stack).

## Tipos de conteúdo proibidos
- Tutoriais de distribuição específicos (Debian, Ubuntu, Red Hat) sem versões upstream, blogs, vídeos ou marketing de fornecedores.
- Modos de uso não oficiais, posts opinativos e conteúdos de terceiros sem vínculo claro com o upstream.

## Estrutura do corpus
- Diretório: `data/knowledge_raw/linux/`
- Subpastas propostas: `kernel/`, `systemd/`, `networking/`, `filesystem/`, `man-pages/`.
- Cada arquivo conterá `source_url`, `captured_at`, `hash` e descrição do conteúdo (ex.: `systemd journald`).

## Workflow de ingestão
1. Capturar os recursos aprovados, convertendo para markdown com metadata e log de hash.
2. Registrar cada fonte no corpus lock antes de qualquer parsing.
3. Documentar adiamentos ou fontes complementares no manifest e no STATUS.
4. Garantir que nenhuma etapa de parsing, chunking ou embeddings seja executada nesta rodada.
