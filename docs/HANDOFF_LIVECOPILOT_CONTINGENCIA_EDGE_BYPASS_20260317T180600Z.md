# Handoff — contingência operacional Edge bypass (2026-03-17T18:06:00Z)

## Objetivo
- restaurar o acesso público ao LiveCopilot desviando temporariamente o tráfego TCP 80/443 direto para o backend `10.45.0.3` enquanto o Edge/Apache no `debian2-1` (.2) permanece fora de serviço.
- registrar esse desvio como atividade operacional provisória e documentar a condição de reversão caso o host .2 volte ou uma nova arquitetura seja estabelecida.

## Contexto e diagnóstico
- o host `debian2-1` (.2) caiu após queda de energia e concentrava a terminação TLS/Apache para `livecopilot.escossio.dev.br`; sem esse Edge o domínio responde `503 Service Unavailable` com `server: cloudflare` e HTML gerado pelo Apache externo (evento registrado em `docs/HANDOFF_LIVECOPILOT_MIKROTIK_PUBLISHED_VALIDATION_20260315T013120Z.md:1-46`).
- o backend `10.45.0.3` continua vivo e expõe `uvicorn` em `0.0.0.0:8099` e `cloudflared` já mapeava `livecopilot.escossio.dev.br` para esse serviço (`docs/HANDOFF_LIVECOPILOT_PUBLIC_DEPLOYMENT_20260313T191538Z.md:7-17` e `docs/HANDOFF_LIVECOPILOT_BACKEND_BIND_0_0_0_0_8099_20260315T022500Z.md:13-34`).

## Ajustes necessários na .3
- confirmar que `uvicorn` ainda responde em `10.45.0.3:8099` e aceita conexões externas (já validado anteriormente via `curl http://10.45.0.3:8099/health` resultando em HTTP 200, conforme `docs/HANDOFF_LIVECOPILOT_BACKEND_BIND_0_0_0_0_8099_20260315T022500Z.md:13-34`).
- garantir que `cloudflared` está ativo e com ingress para `livecopilot.escossio.dev.br` redirecionando para `localhost:8099` (ver `docs/HANDOFF_LIVECOPILOT_MIKROTIK_PUBLISHED_VALIDATION_20260315T013120Z.md:11-62`).
- manter certificado TLS e headers no `cloudflared`/proxy já existente; o TLS era originalmente terminado no Edge, mas o túnel mantém o certificado LetsEncrypt e o host header correto porque o domínio continua listado no `ingress` configurado em `/etc/cloudflared/config.yml`.
- garantir que o firewall local permite 80/443 para o processo `cloudflared` (o binário já roda com `systemctl` e expõe portas definidas no config; a configuração anterior já permitia tráfego público, portanto basta confirmar que as regras não foram modificadas durante a indisponibilidade).

## Mudança de dst-nat no MikroTik
- a regra antiga (`dst-nat tcp dst-port=80,443 to-addresses=debian2-1`) vai ganhar duas cópias provisórias que apontam para `10.45.0.3`; registrar a origem (alias `debian2-1` / IP conhecido) e o novo destino diretamente no RouterOS:
```
/ip firewall nat
set [find comment="LiveCopilot HTTP" ] to-addresses=10.45.0.3
set [find comment="LiveCopilot HTTPS" ] to-addresses=10.45.0.3
```
- caso a regra antiga não possa ser editada diretamente, adicionar regras temporárias com comentários `contingencia-edge-bypass` que capturam o mesmo `dst-address`/`dst-port` e fazem o dst-nat para `10.45.0.3`.
- registrar nas anotações da mudança que o destino original `.2` deve ser restaurado assim que o host de borda voltar ao ar.

## Validação de acesso
- `curl -s http://10.45.0.3:8000/health` falhou daqui (sem rota para a rede privada), mas os documentos acima já documentam a resposta `200` local; a falta de acesso direto aqui é esperada no ambiente de laboratório.
- após o dst-nat ser aplicado, reexecutar:
  - `curl -I https://livecopilot.escossio.dev.br/health`
  - `curl -I https://livecopilot.escossio.dev.br/` e `curl -X POST https://livecopilot.escossio.dev.br/api/chat` com dados testes para garantir HTTP/HTTPS e o certificado TLS que o Cloudflare/Apache entregam agora seguem na ponte `cloudflared`.
- confirmar que o app responde JSON em `/api/chat` com o backend `mikrotik_connector`, conforme havia sido observado localmente (`docs/HANDOFF_LIVECOPILOT_MIKROTIK_PUBLISHED_VALIDATION_20260315T013120Z.md:26-46`).

## Riscos e reversão
- o bypass expõe a .3 diretamente por trás de `cloudflared` sem o buffer adicional de Apache; isso reduz a camada de proteções de proxy e aumenta o blast radius caso o backend tenha falha.
- revertendo a contingência exige:
  1. restaurar as regras `dst-nat` para `debian2-1` (ou remover as regras temporárias). 
  2. confirmar que o Edge/Apache no host .2 voltou com TLS/Apache vivos.
  3. restartar `cloudflared` se a rota original usava um split de domínios diferente.
