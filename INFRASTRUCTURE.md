# AREAL-NEVA-CORE / AI ORCHESTRA — FULL INFRASTRUCTURE STATE (23.03.2026)

## 🔗 1. ИСТОЧНИКИ ИСТИНЫ (SSOT)
- GitHub: https://github.com/rj7hmz9cvm-lgtm/areal-neva-core
- Google Drive: https://drive.google.com/drive/folders/13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB

## 🌐 2. СЕРВЕР И СЕТЬ (Aeza, Ubuntu 24.04 LTS)
- VPN / SSH IP: 89.22.225.136
- API IP: 89.22.227.213:8080
- Kernel fix: net.ipv4.ip_nonlocal_bind=1 (/etc/sysctl.d/99-nonlocal-bind.conf)
- Автоподнятие IP: systemd-сервис /etc/systemd/system/orchestra-ip.service

## 🛡️ 3. VPN (WireGuard)
- Порт: 51820
- Подсеть: 10.0.10.0/24
- Сервер: 10.0.10.1
- Клиент: 10.0.10.2/32
- Конфиг клиента (пример):
  [Interface]
  PrivateKey = <client_private_key>
  Address = 10.0.10.2/24
  DNS = 1.1.1.1, 8.8.8.8
  MTU = 1280
  [Peer]
  PublicKey = <server_public_key>
  Endpoint = 89.22.225.136:51820
  AllowedIPs = 0.0.0.0/0
  PersistentKeepalive = 25

## 🤖 4. AI ORCHESTRA (API)
- URL: http://89.22.227.213:8080
- Метод: POST JSON {"prompt":"задача"}
- Архитектура: Flask (без gunicorn), threading.Lock, subprocess.run → ask_ai.py, таймаут 1800 сек.
- Контейнер: areal-orchestra-live

## 📂 5. ЛОКАЛЬНАЯ СТРУКТУРА
- Рабочая: /root/.areal-neva-core
- Общая: /root/AI_ORCHESTRA

## 🛠️ 6. ДИАГНОСТИКА
curl -s http://89.22.227.213:8080
curl -X POST http://89.22.227.213:8080 -H 'Content-Type: application/json' -d '{"prompt":"тест"}'
docker logs --tail=50 areal-orchestra-live
