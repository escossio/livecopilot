# Handoff - LiveUI lab target stop previsivel

## Contexto
O `liveui-lab.target` parava o target, mas as units do laboratorio permaneciam ativas, exigindo parada manual unit por unit.

## Diagnostico
- target tinha apenas `Wants=` para as services.
- services nao tinham `PartOf=liveui-lab.target`, entao o stop do target nao propagava para elas.

## Correcao aplicada
- Adicionado `PartOf=liveui-lab.target` em:
  - `/etc/systemd/system/liveui-xvfb.service`
  - `/etc/systemd/system/liveui-xfce.service`
  - `/etc/systemd/system/liveui-x11vnc.service`
  - `/etc/systemd/system/liveui-novnc.service`

## Validacao
- `systemctl daemon-reload`
- `systemctl stop liveui-lab.target` => todas as units do laboratorio ficaram `inactive` (x11vnc marcou `failed` no stop, mas parou)
- `systemctl start liveui-lab.target` => todas as units `active`
- `systemctl restart liveui-lab.target` => reinicio coerente
- noVNC:
  - `curl -I http://10.45.0.3:6081/vnc.html` -> `HTTP 200`
- smoke do chat apos restart:
  - `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T045952966Z.png`
  - `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T045952966Z.png`
  - `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T045952966Z.json`

## Backups
- `/etc/systemd/system/liveui-xvfb.service.bak.20260315T045906Z`
- `/etc/systemd/system/liveui-xfce.service.bak.20260315T045906Z`
- `/etc/systemd/system/liveui-x11vnc.service.bak.20260315T045906Z`
- `/etc/systemd/system/liveui-novnc.service.bak.20260315T045906Z`
- `STATUS.md.bak.20260315T050023Z`

## Observacoes
- `liveui-x11vnc.service` marcou `failed` no stop (exit code 2), mas voltou a `active` no start seguinte.
- Nenhuma alteracao no backend principal, voz ou MikroTik.
