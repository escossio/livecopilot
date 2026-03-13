# HANDOFF_LIVECOPILOT_PUBLIC_DEPLOYMENT_20260313T191538Z

status final
- concluido

arquitetura atual
- aplicacao Livecopilot servida por `uvicorn` no backend interno `10.45.0.3:8000`
- publicacao externa feita por Apache como reverse proxy
- trafego publico servido em HTTPS no dominio `livecopilot.escossio.dev.br`

hostname publico
- `livecopilot.escossio.dev.br`

backend interno
- `10.45.0.3:8000`

proxy Apache
- reverse proxy ativo para publicacao do backend web
- proxy de WebSocket funcional em `/ws`

certificado
- TLS ativo com Let's Encrypt

websocket
- upgrade validado via proxy com resposta `101 Switching Protocols`
- canal `/ws` operacional para a interface publicada

status da interface
- interface publica acessivel em HTTPS
- fluxo de texto funcional
- fluxo de voz funcional

limitacoes atuais
- esta rodada nao alterou arquitetura nem configuracao operacional
- o snapshot registra um repositório com varias mudancas locais ja existentes antes desta preservacao
- validacao desta rodada foi de registro/versionamento do estado, nao de nova implantacao

proximos passos possiveis
- iniciar nova rodada de desenvolvimento a partir deste checkpoint versionado
- separar futuras mudancas por tema para reduzir drift de branch
- adicionar validacoes operacionais publicas recorrentes para HTTPS, `/api/chat` e `/ws`
