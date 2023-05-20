from telethon.tl.types import User, Channel
from telethon.tl.functions.channels import GetAdminedPublicChannelsRequest
from .. import loader, utils

@loader.tds
class LinksMod(loader.Module):
    """Retrieve links to all chats, channels, private messages (id), bots and open groups/chats where the user is an owner."""

    strings = {"name": "Links (all chat in .html)"}

    def __init__(self):
        self.client = None

    async def client_ready(self, client, db):
        self.client = client

    async def find_chats(self, user_id):
        dialogs = await self.client.get_dialogs()
        chat_links = []
        for dialog in dialogs:
            if isinstance(dialog.entity, Channel) and dialog.entity.username:
                channel_username = "@" + dialog.entity.username
                chat_links.append(channel_username)
            elif isinstance(dialog.entity, User) and not dialog.entity.bot:
                chat_links.append(str(dialog.entity.id))
        return chat_links

    async def find_channels(self, user_id):
        dialogs = await self.client.get_dialogs()
        channel_links = []
        for dialog in dialogs:
            if isinstance(dialog.entity, Channel) and dialog.entity.username:
                channel_username = "@" + dialog.entity.username
                channel_links.append(channel_username)
        return channel_links

    async def find_private_messages(self, user_id):
        dialogs = await self.client.get_dialogs()
        private_message_links = []
        for dialog in dialogs:
            if isinstance(dialog.entity, User) and not dialog.entity.bot:
                private_message_links.append(str(dialog.entity.id))
        return private_message_links

    async def find_bots(self, user_id):
        dialogs = await self.client.get_dialogs()
        bot_links = []
        for dialog in dialogs:
            if isinstance(dialog.entity, User) and dialog.entity.bot:
                username = dialog.entity.username
                if username:
                    bot_link = f"@{username}"
                    bot_links.append(bot_link)
        return bot_links

    async def find_admined_groups(self):
        result = await self.client(GetAdminedPublicChannelsRequest())
        admined_group_links = []
        for obj in result.chats:
            if obj.username:
                admined_group_links.append(f'<a href="https://t.me/{obj.username}">{obj.title}</a>')
        return admined_group_links

    @loader.owner
    async def allchatlinkscmd(self, message):
        """Retrieve links to all chats, channels, private messages (id), bots and open groups/chats where the user is an owner."""
        user_id = message.from_id
        chat_links = await self.find_chats(user_id)
        channel_links = await self.find_channels(user_id)
        private_message_links = await self.find_private_messages(user_id)
        bot_links = await self.find_bots(user_id)
        admined_group_links = await self.find_admined_groups()

        result = []
        if chat_links:
            result.append("<b>All chats:</b>\n" + "\n".join(chat_links))
        if channel_links:
            result.append("<b>Channels:</b>\n" + "\n".join(channel_links))
        if private_message_links:
            result.append("<b>Private Messages:</b>\n" + "\n".join(private_message_links))
        if bot_links:
            result.append("<b>Bots:</b>\n" + "\n".join(bot_links))
        if admined_group_links:
            result.append("<b>Owner Open Groups/Chats:</b>\n" + "\n".join(admined_group_links))

        result_text = "\n\n".join(result)
        with open("result.html", "w") as file:
            file.write(result_text)

        await message.client.send_file(
            message.chat_id,
            "result.html",
            caption="Links to chats, channels, private messages, bots, and admined groups/chats.",
            parse_mode="HTML"
        )

        import os
        os.remove("result.html")
