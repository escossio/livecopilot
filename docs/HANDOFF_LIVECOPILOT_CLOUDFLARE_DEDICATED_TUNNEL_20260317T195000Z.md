# Handoff LiveCopilot Cloudflare Dedicated Tunnel (2026-03-17T19:50:00Z)

## Context
- o host de borda `debian2-1` (.2) permanece indisponível após a queda de energia, deixando o domínio `livecopilot.escossio.dev.br` exposto ao HTTP/2 521 apesar do backend em `10.45.0.3` and dos proxies locais já operando.
- como tentativa de contingência, criamos um tunnel Cloudflare exclusivamente dedicado ao hostname `livecopilot.escossio.dev.br`, mantendo o tunnel legado `agente` intacto para `agente.escossio.dev.br`.

## Ações realizadas
- `cloudflared tunnel create livecopilot-tunnel` → novo tunnel `98c4d32f-62d3-42f1-b28b-d49d58383a0b`, credenciais copiadas para `/etc/cloudflared/livecopilot-tunnel.json`.
- `cloudflared tunnel route dns livecopilot-tunnel livecopilot.escossio.dev.br` falhou (código 1003) porque já existe um registro DNS `livecopilot.escossio.dev.br` apontando para o tunnel antigo; não é possível sobrescrever via CLI nesta versão sem antes remover o registro existente no painel Cloudflare.
- criada configuração dedicada `/etc/cloudflared/livecopilot-config.yml` apontando `livecopilot.escossio.dev.br` para `http://127.0.0.1:8080`, validada com `cloudflared tunnel --config ... ingress validate`.
- testamos execução em foreground (`timeout 20 cloudflared --config ... tunnel run`) e mantivemos o tunnel como serviço systemd `cloudflared-livecopilot.service` para garantir persistência sem impactar o tunnel legado.

## Estado atual
- serviço `cloudflared-livecopilot.service` ativo e registrando conexões QUIC com as bordas `gig09`/`jdo01` a partir do connector `fead993b-e02e-4783-b4e1-07ffb04c1118`.
- apesar do tunnel dedicado operar corretamente, o domínio ainda responde HTTP/2 521, pois o CNAME público ainda resolve para o tunnel antigo (`agente`). O acesso externo continua bloqueado até que o DNS seja atualizado para o novo tunnel.

## Próximos passos (completados)
1. o registro DNS `livecopilot.escossio.dev.br` foi atualizado manualmente no painel Cloudflare para apontar para o tunnel `livecopilot-tunnel`.  
2. o tunnel `agente` foi mantido intacto para `agente.escossio.dev.br`, garantindo que o domínio legado permaneça estável.  
3. após a reatribuição do DNS, revalidamos o domínio (`curl -I` e `curl -s /health`). O HEAD ainda devolve HTTP/2 405 porque o endpoint exige GET, mas o GET retorna `{"status":"ok"}` e confirma que o 521 desapareceu.

## Revalidação
- Cabe ressaltar que a borda agora responde `HTTP/2 405` ao `HEAD /health` (permitido apenas GET).  
- O GET `https://livecopilot.escossio.dev.br/health` retorna `{"status":"ok"}`, provando que o backend está acessível via Cloudflare Tunnel dedicado e que a contingência está concluída.
