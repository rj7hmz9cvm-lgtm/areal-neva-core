import logging
from pathlib import Path
from telethon import TelegramClient

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.clients = {}

    async def load_session(self, phone: str, api_id: int, api_hash: str) -> TelegramClient:
        session_path = self.sessions_dir / f"{phone}"
        client = TelegramClient(str(session_path), api_id, api_hash)
        
        await client.connect()
        if not await client.is_user_authorized():
            logger.warning(f"Session for {phone} not authorized. Manual login required.")
            # В интерактивном режиме здесь можно добавить ввод кода, 
            # но для сервера сессии лучше готовить заранее.
        
        self.clients[phone] = client
        return client

    async def remove_session(self, phone: str):
        if phone in self.clients:
            await self.clients[phone].disconnect()
            del self.clients[phone]

    async def close_all(self):
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()
