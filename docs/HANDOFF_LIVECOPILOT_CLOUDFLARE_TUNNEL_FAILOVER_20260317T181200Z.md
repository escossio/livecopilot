# Handoff — failover do Cloudflare Tunnel (2026-03-17T18:12:00Z)

## Objetivo
- garantir que `livecopilot.escossio.dev.br` continue ativo mesmo com o Edge/Apache (.2) fora ar e apenas com o Cloudflare Tunnel rodando no host do LiveCopilot (.3).

## Túnel confirmado
- o domínio já estava mapeado no ingresso do túnel Cloudflare (`/etc/cloudflared/config.yml` contém `livecopilot.escossio.dev.br` apontando para `http://127.0.0.1:8099`, conforme `cat /etc/cloudflared/config.yml`).
- as credenciais do túnel ficam em `/etc/cloudflared/6394a032-08e8-4bc7-a957-44c77e743c49.json` e o túnel registra conexões HTTP/2 com os IPs das bordas do Cloudflare, portanto basta manter o serviço ativo.

## Ajustes aplicados na .3
- verifiquei que o backend local responde `curl -s http://127.0.0.1:8099/health` com `{"status":"ok"}`, o que é a mesma porta utilizada pelo túnel (`docs/HANDOFF_LIVECOPILOT_BACKEND_BIND_0_0_0_0_8099_20260315T022500Z.md:13-34`).
- o serviço `cloudflared` já está habilitado e em execução (`systemctl status cloudflared` mostra `Active: active (running)` com o binário `cloudflared --config /etc/cloudflared/config.yml tunnel run`). Nenhuma instalação nova foi necessária.

## Estado do acesso externo
- a mudança de dst-nat anterior garantiu que o tráfego 80/443 não passasse mais pelo Edge, e agora o Cloudflare Tunnel é a única camada de exposição (a mesma usada antes da queda, descrita em `docs/HANDOFF_LIVECOPILOT_PUBLIC_DEPLOYMENT_20260313T191538Z.md:7-17`).
- os próximos passos de validação são os mesmos do failover anterior: `curl -I https://livecopilot.escossio.dev.br/health`, `curl -I https://livecopilot.escossio.dev.br/`, e um `POST /api/chat` para garantir HTTP/HTTPS e resposta JSON.

## Pendências e reversão
- manter o Tunnel ativo até que o Edge/Apache (.2) volte com TLS; a reversão implica restaurar `dst-nat` para `.2` e confirmar que `cloudflared` ainda aponta para o backend local.
- caso o túnel precise ser recriado, usar a mesma credencial e ingress para preservação do hostname e dos headers originais.
