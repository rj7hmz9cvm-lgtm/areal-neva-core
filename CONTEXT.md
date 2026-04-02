# AI ORCHESTRA — КОНТЕКСТ ДЛЯ НОВОГО ЧАТА

## 🌐 СЕРВЕР
- VPN IP: 89.22.225.136 (WireGuard, порт 51820)
- Оркестр IP: 89.22.227.213:8080 (Docker, Flask)

## 🛡️ VPN (WireGuard)
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

## 🤖 ОРКЕСТР
- URL: http://89.22.227.213:8080
- Метод: POST JSON {"prompt":"задача"}
- Ответ: JSON {"ok": true, "stdout": "...", "stderr": "..."}
- Логи: docker logs --tail=50 areal-orchestra-live

## 📂 СТРУКТУРА
- Репозиторий: https://github.com/rj7hmz9cvm-lgtm/areal-neva-core
- Рабочая папка: /root/.areal-neva-core
- Общая папка: /root/AI_ORCHESTRA

## 🔧 УПРАВЛЕНИЕ
curl http://89.22.227.213:8080
curl -X POST http://89.22.227.213:8080 -H 'Content-Type: application/json' -d '{"prompt":"твой запрос"}'
docker logs --tail=50 areal-orchestra-live
cd /root/.areal-neva-core && docker compose -f docker-compose.orchestra.yml down && docker compose -f docker-compose.orchestra.yml up -d --build

## ✅ СТАТУС
Оркестр принимает задачи, VPN работает. Всё готово.
