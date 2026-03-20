# Handoff — contingência Cloudflare Tunnel (2026-03-17T18:30:00Z)

## Diagnóstico
- o host `debian2-1` (.2) segue fora do ar após queda de energia, e o Cloudflare Tunnel hospedado em `10.45.0.3` é a única camada que pode manter `livecopilot.escossio.dev.br` exposto.
- `/etc/cloudflared/config.yml` já mapeava `livecopilot.escossio.dev.br` para `http://127.0.0.1:8099`, com a credencial em `/etc/cloudflared/6394a032-08e8-4bc7-a957-44c77e743c49.json`; o túnel opera em HTTP/2 sem QUIC e está configurado para `ingress` fixo.
- os logs públicos do `cloudflared` (capturados via `journalctl -u cloudflared -n 200`) revelam ciclos constantes de `Error shutting down control stream` e `context canceled`, mas o túnel registra reconexões imediatamente; isso sugere que o Cloudflare Edge está encerrando a sessão antes que a origem responda.

## Ajustes aplicados na .3
- `cloudflared` permanece instalado e habilitado como serviço (`systemctl status cloudflared --no-pager`); o binário é executado com `cloudflared --config /etc/cloudflared/config.yml tunnel run` sem alterações adicionais.
- validado que o backend `uvicorn` em `127.0.0.1:8099` responde localmente (`curl -s http://127.0.0.1:8099/health` → `{"status":"ok"}`) e que o cabeçalho GET/HEAD (405 para HEAD) coincide com a porta usada pelo túnel.
- nenhuma modificação de código ou script foi necessária: mantivemos o mesmo `cloudflared` e `uvicorn` já instalados, apenas confirmamos o estado atual.

## Estado do dst-nat (MikroTik)
- o desvio temporário já documentado em `docs/HANDOFF_LIVECOPILOT_CONTINGENCIA_EDGE_BYPASS_20260317T180600Z.md` segue ativo: o MikroTik encaminha 80/443 para `10.45.0.3`, garantindo que o túnel é a rota de entrada pública enquanto `.2` permanece offline.

## Validação externa
- `systemctl status cloudflared --no-pager` → serviço `active (running)` há 16+ horas (PID 740, CGroup configurado) apesar das reconexões registradas nas bordas do Cloudflare.
- `curl -I https://livecopilot.escossio.dev.br/health` → resposta HTTP/2 521 (Cloudflare) com corpo `15` bytes, sinalizando que a borda não consegue abrir o túnel corretamente.
- `curl -I https://livecopilot.escossio.dev.br/` → também HTTP/2 521 com os mesmos cabeçalhos `server: cloudflare` e `cf-ray` distintos.
- `curl -I http://127.0.0.1:8099/health` → 405 Method Not Allowed (allow GET) e `curl -s` retorna `{"status":"ok"}`, provando que o backend está saudável e operando.
## Logs e validações operacionais
- `journalctl -u cloudflared -n 200 --no-pager` → os eventos mais recentes repetem `Error shutting down control stream` e `context canceled`, confirmando que cada reconexão começa mas a borda encerra a sessão antes de encaminhar a requisição.
- `cloudflared tunnel --config /etc/cloudflared/config.yml ingress validate` → OK, indicando que o `ingress` definido em `/etc/cloudflared/config.yml` é sintaticamente válido e o hostname `livecopilot.escossio.dev.br` está autorizado.

## Pendências e próximos passos
- investigar os motivos do 521: revisar `journalctl -u cloudflared` nos últimos minutos, rodar `cloudflared tunnel ingress validate` para confirmar que o ingresso está estável e que o certificado TLS será servido corretamente.
- garantir que nenhum firewall/iptables bloqueia a porta 8099 (local) ou a comunicação `cloudflared` → Cloudflare; os logs sugerem que as conexões são encerradas (`context canceled`), então pode ser necessário reiniciar o túnel após a validação.
- validar externamente novamente depois desses ajustes com `curl -I https://livecopilot.escossio.dev.br/` e com um POST para `/api/chat` para assegurar respostas JSON.
- manter essa configuração até `.2` retornar e então restaurar o dst-nat para o Edge e recompor o proxy original.
