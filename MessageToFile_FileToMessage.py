from .. import loader, utils
import io

class MTFMod(loader.Module):
    """Отправляет сообщение в виде файла // отправляет файл в виде сообщения."""
    strings = {'name': 'MessageToFile_FileToMessage'}

    async def mtfcmd(self, message):
        """
        .mtf <в ответ на текст>
        
        Отправляет сообщение в виде текстового файла.
        """
        await self._process_mtf_command(message, file_ext=".txt")

    async def mtfpycmd(self, message):
        """
        .mtfpy <в ответ на текст>
        
        Отправляет сообщение в виде файла с расширением .py.
        """
        await self._process_mtf_command(message, file_ext=".py")

    async def _process_mtf_command(self, message, file_ext):
        reply = await message.get_reply_message()
        if not reply or not reply.message:
            await message.edit("<b>Ответьте на текст!</b>")
            return 
        text = bytes(reply.raw_text, "utf8")
        fname = utils.get_args_raw(message) or str(message.id+reply.id)+file_ext
        file = io.BytesIO(text)
        file.name = fname
        file.seek(0)
        await reply.reply(file=file)
        await message.delete()

    async def ftmcmd(self, message):
        """
        .ftm <в ответ на файл>
        
        Отправляет содержимое файла в виде сообщения.
        """
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await message.edit("<b>Ответьте на файл!</b>")
            return 
        text = await reply.download_media(bytes)
        text = str(text, "utf8")
        if utils.get_args(message):
            text = f"<code>{text}</code>"
        await utils.answer(message, utils.escape_html(text))