# HANDOFF LIVECOPILOT LIVEUI VISUAL LAB BASE 20260315T003401Z

## Status final

- Laboratorio visual persistente criado no mesmo host do backend, isolado no usuario `liveui`
- Backend principal `livecopilot-semantic-api.service` permaneceu intacto e ativo
- Sessao grafica XFCE, VNC local e noVNC interno estao ativos e persistentes via systemd
- Browser visual funcional: `firefox-esr`
- Base de automacao funcional: `playwright` com Firefox

## O que foi feito

- criado usuario `liveui`
- criada estrutura em `/srv/liveui`
- instalada stack `Xvfb + XFCE + x11vnc + noVNC/websockify`
- instalados `chromium` e `firefox-esr`
- mantido `chromium` como base instalada, mas com limitacao operacional no host
- instalado `playwright` local em `/srv/liveui/automation`
- criado smoke `smoke-homepage.js`
- criados services:
  - `liveui-xvfb.service`
  - `liveui-xfce.service`
  - `liveui-x11vnc.service`
  - `liveui-novnc.service`
  - `liveui-lab.target`
- desabilitado `lightdm` para nao interferir no host

## Validacao real

- `systemctl is-active livecopilot-semantic-api.service` -> `active`
- `systemctl is-active liveui-lab.target liveui-xvfb.service liveui-xfce.service liveui-x11vnc.service liveui-novnc.service` -> todos `active`
- `systemctl is-enabled liveui-lab.target` -> `enabled`
- `curl -I http://10.45.0.3:6081/vnc.html` -> `HTTP/1.1 200 OK`
- `runuser -u liveui -- /srv/liveui/scripts/open-livecopilot.sh`
  - abriu Firefox ESR na sessao do `liveui`
- `runuser -u liveui -- /srv/liveui/scripts/run-playwright-smoke.sh`
  - `title=livecopilot`
  - screenshot: `/srv/liveui/artifacts/livecopilot-homepage.png`
- listeners observados:
  - `127.0.0.1:5901` -> `x11vnc`
  - `10.45.0.3:6081` -> `websockify`
  - `0.0.0.0:8099` -> `uvicorn` do backend

## URL interna

- `http://10.45.0.3:6081/vnc.html?host=10.45.0.3&port=6081&autoconnect=1&resize=remote`

## Comandos operacionais

- iniciar: `systemctl start liveui-lab.target`
- parar: `systemctl stop liveui-lab.target`
- reiniciar: `systemctl restart liveui-lab.target`
- abrir Livecopilot na sessao: `runuser -u liveui -- /srv/liveui/scripts/open-livecopilot.sh`
- smoke minimo de automacao: `runuser -u liveui -- /srv/liveui/scripts/run-playwright-smoke.sh`

## Limitacoes

- `chromium` do Debian 13 neste host cai antes de abrir por `chrome_crashpad_handler: --database is required`
- o Chromium do Playwright reproduziu o mesmo erro
- por isso, a base operacional ficou em Firefox para esta rodada

## Arquivos tocados

- `/etc/liveui/lab.env`
- `/etc/systemd/system/liveui-xvfb.service`
- `/etc/systemd/system/liveui-xfce.service`
- `/etc/systemd/system/liveui-x11vnc.service`
- `/etc/systemd/system/liveui-novnc.service`
- `/etc/systemd/system/liveui-lab.target`
- `/srv/liveui/scripts/common.sh`
- `/srv/liveui/scripts/start-xvfb.sh`
- `/srv/liveui/scripts/start-xfce.sh`
- `/srv/liveui/scripts/start-x11vnc.sh`
- `/srv/liveui/scripts/start-novnc.sh`
- `/srv/liveui/scripts/open-livecopilot.sh`
- `/srv/liveui/scripts/run-playwright-smoke.sh`
- `/srv/liveui/automation/package.json`
- `/srv/liveui/automation/package-lock.json`
- `/srv/liveui/automation/smoke-homepage.js`
- `/lab/projects/livecopilot/STATUS.md`
