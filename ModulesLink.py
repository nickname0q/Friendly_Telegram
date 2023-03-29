import io
import inspect

from .. import loader, utils


@loader.tds
class ModulesLinkMod(loader.Module):
    """Ссылка на модуль"""

    strings = {'name': 'ModulesLink'}

    async def mlcmd(self, message):
        """Вывести ссылку на модуль"""

        args = utils.get_args_raw(message)
        if not args:
            return await message.edit('Нет аргументов.')

        await message.edit('Ищем...')

        try:
            module_names = [x.strings["name"] for x in self.allmodules.modules]
            module_name = next((name for name in module_names if name.lower() == args.lower()), None)
            if not module_name:
                return await message.edit(f'Модуль "{args}" не найден.')

            module = next((x for x in self.allmodules.modules if x.strings["name"].lower() == args.lower()), None)
            if not module:
                return await message.edit(f'Не удалось загрузить модуль "{args}".')

            r = inspect.getmodule(module)
            link = str(r).split('(')[1].split(')')[0]

            if link and "http" in link:
                text = f'<a href="{link}">Ссылка</a> на {module_name}: <code>{link}</code>'
            else:
                text = f"Модуль {module_name}"

            out = io.BytesIO(r.__loader__.data)
            out.name = f"{module_name}.py"
            out.seek(0)

            await message.respond(text, file=out)
            await message.delete()
        except Exception as e:
            await message.edit(f"Произошла ошибка: {e}")
