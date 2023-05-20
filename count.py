import datetime
from telethon import types
from .. import loader, utils

@loader.tds
class CountDialogsMod(loader.Module):
    """Counts the number of dialogs in your Telegram account."""

    strings = {"name": "CountDialogs"}

    def __init__(self):
        self.client = None

    async def client_ready(self, client, db):
        self.client = client

    async def countcmd(self, message):
        """Counts the number of dialogs in your Telegram account."""
        start_time = datetime.datetime.now()

        num_users = 0
        num_basic_groups = 0
        num_super_groups = 0
        num_channels = 0
        num_bots = 0
        num_blocked_chats = 0

        info_message = await utils.answer(message, "Getting information...")

        async for dialog in self.client.iter_dialogs():
            if isinstance(dialog.entity, types.User):
                if dialog.entity.bot:
                    num_bots += 1
                else:
                    num_users += 1
            elif isinstance(dialog.entity, types.Channel):
                if dialog.entity.broadcast:
                    num_channels += 1
                else:
                    num_super_groups += 1
            elif isinstance(dialog.entity, types.Chat):
                num_basic_groups += 1
                try:
                    await self.client.get_permissions(dialog)
                except:
                    num_blocked_chats += 1

        end_time = datetime.datetime.now()
        duration_in_seconds = (end_time - start_time).seconds

        await self.client.edit_message(
            message.chat_id,
            info_message[0].id,
            f"My Telegram Account Infos:\n"
            f"Users:\t{num_users}\n"
            f"Basic Groups:\t{num_basic_groups}\n"
            f"Super Groups:\t{num_super_groups}\n"
            f"Channels:\t{num_channels}\n"
            f"Bots:\t{num_bots}\n"
            f"Blocked Chats:\t{num_blocked_chats}\n"
            f"Obtained in {duration_in_seconds} seconds."
        )
