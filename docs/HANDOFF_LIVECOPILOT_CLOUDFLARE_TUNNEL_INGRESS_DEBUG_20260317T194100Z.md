# Handoff LiveCopilot Cloudflare Tunnel Ingress Debug (2026-03-17T19:41:00Z)

## Context
- domínio público `livecopilot.escossio.dev.br` vem do túnel `6394a032-08e8-4bc7-a957-44c77e743c49` que estava operando na borda `debian2-1` (.2) antes da queda.
- desde a contingência, o host `.3` está rodando `uvicorn` em `127.0.0.1:8099`, Apache proxy em `127.0.0.1:8080` e o tunnel `cloudflared` foi configurado para apontar para o proxy.
- mesmo com o backend e o proxy funcionando, as bordas do Cloudflare continuam devolvendo HTTP/2 521 (origin unreachable).

## O que foi verificado
- **Configuração atual** (`/etc/cloudflared/config.yml`):
  - `tunnel`: 6394a032-08e8-4bc7-a957-44c77e743c49
  - `credentials-file`: /etc/cloudflared/6394a032-08e8-4bc7-a957-44c77e743c49.json
  - `protocol: http2`, `no-quic: true`
  - `ingress` com regra explícita para `livecopilot.escossio.dev.br` mapeada para `service: http://127.0.0.1:8080`
  - regra secundária para `agente.escossio.dev.br` e fallback `http_status:404`
- **Connectors ativos** (via `cloudflared tunnel info`):
  - Connector `c5a92578-2267-4131-9034-bc18fa9a5a8f` (linux_amd64 2026.2.0) abriu múltiplas conexões com as bordas `gig09`/`jdo01`.
  - Nenhum connector antigo ou de `.2` aparece listado.
- **Fluxo de ingress**:
  1. Host `livecopilot.escossio.dev.br` → Apache proxy `http://127.0.0.1:8080`
  2. Apache proxy → backend `http://127.0.0.1:8099`
  3. Connector `c5a92578...` sustenta o túnel `agente` entre `.3` e o Cloudflare Edge.

## Ações realizadas
- validado `ingress` com `cloudflared tunnel --config /etc/cloudflared/config.yml ingress validate`
- reiniciado o serviço `systemctl restart cloudflared` e monitorado status (`systemctl status cloudflared --no-pager`)
- os logs mostraram conexões regulares (multiplas conexões HTTP/2 com os nós `gig09` e `jdo01`)
- testes externos:
  - `curl -I https://livecopilot.escossio.dev.br/health` → HTTP/2 521
  - `curl -s https://livecopilot.escossio.dev.br/health` → `error code: 521`
  - `curl -I https://livecopilot.escossio.dev.br/` → HTTP/2 521

## Conclusão parcial
- a configuração local, o Apache e o backend estão respondendo corretamente; os connectors atuais estão ativos e alinhados com o túnel em `.3`.
- o Cloudflare Edge mantém o 521; o bloqueio parece fora do host `.3` (possíveis causas: sessão/host mismatch no lado Cloudflare, questões de edge quota ou certificados expirados).
- este handoff registra a investigação de ingress antes de requisitar suporte do Cloudflare.

## Próximos passos sugeridos
1. Consultar os logs/diagnósticos do lado Cloudflare (Dashboard ou suporte) para o tunnel `6394a032-08e8-4bc7-a957-44c77e743c49` e verificar se há alertas de certificação ou de sessão.
2. Validar se há políticas de hostname extras associadas a `agente.escossio.dev.br` na mesma conta que poderiam confundir o Edge.
3. Caso a borda continue 521, escalar com Cloudflare indicando que o connector está saudável mas ainda recebe `origin unreachable` para `livecopilot.escossio.dev.br`.
