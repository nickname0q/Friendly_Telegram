import logging
import io
import aiohttp

from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from .. import loader, utils
from gettext import gettext as _

logger = logging.getLogger(__name__)


@loader.tds
class WeatherMod(loader.Module):
    """Предоставляет информацию в картинках о погоде с помощью сервиса wttr.in"""
    strings = {'name': 'Weather'}

    async def _get_weather_info(self, location):
        url = f"https://wttr.in/{location}?format=3"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    return (await response.text()).strip()
        except aiohttp.ClientError:
            return None

    @loader.unrestricted
    async def weathercmd(self, message):
        """
        Получает изображение погоды для указанного города.
        Использование: .weather <город>
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, _("Укажите город."))
            return

        weather_info = await self._get_weather_info(args.strip())
        if not weather_info:
            await utils.answer(message, _("Не удалось получить информацию о погоде."))
            return

        text = _("Текущая погода в {weather_info}").format(weather_info=weather_info)
        url = f"https://wttr.in/{args.strip()}.png?m"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await utils.answer(message, text)
                        return
                    content_type = response.headers.get("Content-Type")
                    if not content_type or "image" not in content_type:
                        await utils.answer(message, text)
                        return
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > 10 * 1024 * 1024:
                        await utils.answer(message, _("Файл слишком большой."))
                        return
                    file = io.BytesIO(await response.read())
                    file.name = "weather.png"

                    if message.is_reply:
                        reply_to = message.reply_to_msg_id
                    else:
                        reply_to = None
                    sent_message = await message.client.send_file(
                        message.chat_id,
                        file=file,
                        caption=text,
                        reply_to=reply_to
                    )
                    try:
                        await message.delete()
                    except MessageNotModifiedError:
                        pass
                    return sent_message

        except aiohttp.ClientError:
            await utils.answer(message, _("Не удалось получить изображение погоды."))