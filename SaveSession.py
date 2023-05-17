import logging
import io

from telethon.sessions import StringSession

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class SaveSessionMod(loader.Module):
    """Сохранение сессии в файл, отправка сессии выбранному пользователю. Без аргументов - сессия будет отправлена в текущий чат."""
    strings = {"name": "SaveSession"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def savesscmd(self, message):
        """Сохранить текущую сессию"""
        self.db.set("friendly-telegram", "saved_session", StringSession.save(self.client.session))
        await utils.answer(message, "Текущая сессия сохранена!")

    async def sendsscmd(self, message):
        """Отправить сохраненную сессию другому пользователю"""
        saved_session = self.db.get("friendly-telegram", "saved_session", None)
        if saved_session is None:
            saved_session = StringSession.save(self.client.session)
            self.db.set("friendly-telegram", "saved_session", saved_session)

        if len(message.text.split()) < 2:
            to_user = message.peer_id
            text = "Сессия успешно отправлена в этот чат!"
        else:
            to_user = message.text.split()[1]
            text = "Сессия успешно отправлена пользователю {}!".format(to_user)

        me = await self.client.get_me()
        phone_number = me.phone
        filename = "{}.txt".format(phone_number)

        session_file = io.BytesIO(saved_session.encode())
        session_file.name = filename

        async with self.client.conversation(to_user) as conv:
            await conv.send_file(session_file)

        await utils.answer(message, text)