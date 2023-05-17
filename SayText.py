# requires: gtts
import os
from gtts import gTTS
from telethon.tl.types import DocumentAttributeAudio
from telethon.errors import MessageEmptyError, TimeoutError
from telethon import events
from .. import loader, utils


def register(cb):
    cb(SayTextMod())


class SayTextMod(loader.Module):
    strings = {"name": "SayText"}

    async def saycmd(self, message):
        """.say <текст> - преобразует текст в голосовое сообщение."""
        text = utils.get_args_raw(message)

        if not text:
            reply = await message.get_reply_message()
            if reply and reply.message:
                text = reply.message
            else:
                return await utils.answer(message, "<b>Отсутствует текст или ответное сообщение.</b>")

        sent_message = await utils.answer(message, "<b>Генерация голосового сообщения...</b>")

        try:
            tts = gTTS(text, lang="ru")
            tts.save("say.ogg")

            voice = await message.client.upload_file("say.ogg")

            await message.client.send_file(
                message.chat_id,
                voice,
                voice_note=True,
                reply_to=message.id,
                attributes=[DocumentAttributeAudio(duration=0)],
                timeout=60,
            )

        except (MessageEmptyError, TimeoutError):
            return await utils.answer(message, "<b>Не удалось отправить голосовое сообщение.</b>")

        finally:
            os.remove("say.ogg")
            await sent_message[0].delete()