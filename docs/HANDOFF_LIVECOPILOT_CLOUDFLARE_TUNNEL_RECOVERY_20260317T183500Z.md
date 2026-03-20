# Handoff — recuperação do Cloudflare Tunnel (2026-03-17T18:35:00Z)

## Objetivo
- investigar e documentar por que o túnel Cloudflare em `10.45.0.3` não entrega `livecopilot.escossio.dev.br`, tentando um restart limpo, execução em foreground e checagem de rede/firewall antes de decidir se o bloqueio é externo.

## Restart e testes iniciais
- executei `systemctl restart cloudflared` e confirmei `Active: active (running)` com PID 110024; o `journalctl -u cloudflared -n 100 --no-pager` continua mostrando ciclos de `Error shutting down control stream` / `context canceled` após cada reconexão.
- após o restart, `curl -I https://livecopilot.escossio.dev.br/health` e `curl -s https://livecopilot.escossio.dev.br/health` ainda retornaram HTTP/2 521 (Cloudflare). O backend `127.0.0.1:8099` responde `{"status":"ok"}` ao GET, ou seja, a porta continua ativa.

## Execução em foreground
- parei o serviço (`systemctl stop cloudflared`) e rodei `timeout 20 cloudflared --config /etc/cloudflared/config.yml tunnel run` manualmente para capturar logs. Ele registra o mesmo túnel `6394a032-08e8-4bc7-a957-44c77e743c49`, conecta nas bordas `198.41.200.53/193` e não emite erros adicionais durante os 20 segundos úteis; ao fim o timeout encerra o processo sem revelar um stack trace diferente.

## Diagnóstico de rede/firewall
- `curl -I https://www.cloudflare.com` e `curl -I https://www.google.com` funcionam, `ip route` aponta para `default via 10.45.0.1`, `iptables -S` e `iptables -L -n -v` mostram policies ACCEPT, e `nft list ruleset` está vazio.
- o diretório `/etc/cloudflared/` mantém o mesmo UUID `6394a032-08e8-4bc7-a957-44c77e743c49.json` e o `config.yml` não mudou (nomeados ingress para `livecopilot.escossio.dev.br` e `agente.escossio.dev.br`).

## Validação externa final
- após religar o serviço (`systemctl start cloudflared` + `systemctl enable cloudflared`), revalidei com `curl -I https://livecopilot.escossio.dev.br/health` (HTTP/2 521) e `curl -s https://livecopilot.escossio.dev.br/health` (`error code: 521`). O Cloudflare ainda não consegue entregar o tráfego ao túnel.

## Próximos passos sugeridos
- esta investigação confirma que o host `.3` tem rede/porta/firewall ok, que o túnel inicia e registra conexões e que o backend local responde, mas o Edge do Cloudflare descarta a sessão (521). Recomendo escalonar a análise para o time de rede/Cloudflare para verificar certificados, quotas ou bloqueios de origem, e só então considerar recriar o túnel se a credencial atual estiver comprometida.
