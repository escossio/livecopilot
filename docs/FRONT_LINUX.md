# FRONT LINUX

## Objetivo
- Formalizar a frente Linux para apoiar knowledge retrieval em administração, systemd, processos, redes e sistemas de arquivos, seguindo o lifecycle formal antes de rodar parsing ou chunking.

## Escopo
- Domínio: documentação oficial do kernel, systemd, ferramentas de rede e filesystem, guias de segurança e operações do Linux upstream.
- Exclusões: blogs, vídeos, cursos de marketing, e conteúdos de distribuição específicos que não sejam parte da documentação upstream oficial (kernel.org, freedesktop.org, man7.org).

## Source policy
- Fontes permitidas: kernel.org (documentação e manuais), freedesktop.org (systemd, dbus, etc) e man7.org (páginas de manual mantidas oficialmente).
- Conteúdo deve ser técnico, com foco em operações e comandos, evitando artigos promocionais ou de soluções proprietárias.
- Idioma preferido: inglês; traduções oficiais podem ser consideradas se mantidas pela própria comunidade upstream.

## Source manifest (inicial)
- Kernel Documentation (`https://www.kernel.org/doc/html/latest/`) – kernel subsystems e interfaces.
- systemd Documentation (`https://www.freedesktop.org/wiki/Software/systemd/` e `https://www.freedesktop.org/software/systemd/man/systemd.html`) – unit files, journal, timers, networkd.
- Linux Networking (`https://www.kernel.org/doc/html/latest/networking/`) – protocols e ferramentas.
- Filesystems & Storage (`https://www.kernel.org/doc/html/latest/filesystems/`).
- man7 pages (`https://man7.org/linux/man-pages/dir_section_1.html`) – comandos essenciais (ps, top, ip, journalctl).

## Corpus lock (inicial)
- URLs acima são as fontes aprovadas; o lock será formalizado assim que o corpus preparation registrar os arquivos e hashes correspondentes.
- Fora do lock: conteúdos de distribuições específicas (Red Hat, Debian, Ubuntu) que não sejam diretamente derivados da documentação upstream, tutoriais de terceiros e vídeos.

## Status
- state: `closed`
- stage: `closure_decision`
- próximo passo: monitorar atualizações upstream e reativar se houver mudanças de kernel/systemd.

## Lifecycle oficial
- Pipeline completo documentado em `docs/FRONT_LIFECYCLE_CONTRACT.md`; a frente chegou ao término em `closure_decision`.

## Observação
- Nenhuma ingestão, parsing ou chunking foi executado; documentamos apenas o plano inicial.
