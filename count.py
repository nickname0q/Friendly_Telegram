from telethon import events
from datetime import datetime
from telethon.tl.types import User, Chat, Channel
from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern="count"))
async def count_dialogs(event):
    if event.fwd_from:
        return

    start_time = datetime.now()

    num_users = 0
    num_basic_groups = 0
    num_super_groups = 0
    num_channels = 0
    num_bots = 0
    num_blocked_chats = 0

    await event.edit("Getting information...")

    async for dialog in borg.iter_dialogs():
        if isinstance(dialog.entity, User):
            if dialog.entity.bot:
                num_bots += 1
            else:
                num_users += 1
        elif isinstance(dialog.entity, Channel):
            if dialog.entity.broadcast:
                num_channels += 1
            else:
                num_super_groups += 1
        elif isinstance(dialog.entity, Chat):
            num_basic_groups += 1
            try:
                await borg.get_permissions(dialog)
            except:
                num_blocked_chats += 1
        else:
            logger.info(dialog.stringify())

    end_time = datetime.now()
    duration_in_seconds = (end_time - start_time).seconds

    await event.edit(
        f"My Telegram Account Infos:\n"
        f"Users:\t{num_users}\n"
        f"Basic Groups:\t{num_basic_groups}\n"
        f"Super Groups:\t{num_super_groups}\n"
        f"Channels:\t{num_channels}\n"
        f"Bots:\t{num_bots}\n"
        f"Blocked Chats:\t{num_blocked_chats}\n"
        f"Obtained in {duration_in_seconds} seconds."
    )
