import re
import random
import hashlib
import requests
import logging
from requests.structures import CaseInsensitiveDict
from telethon import events
from .. import loader, utils

class GameCheatsLib:
    async def get_token(self, g):
        headers = CaseInsensitiveDict()
        headers["Host"] = "api.service.gameeapp.com"
        headers["Connection"] = "keep-alive"
        headers["Content-Length"] = "224"
        headers["client-language"] = "en"
        headers["x-install-uuid"] = "0c1cd354-302a-4e76-9745-6d2d3dcf2c56"
        headers["sec-ch-ua-mobile"] = "?0"
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        headers["sec-ch-ua-platform"] = "Windows"
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "*/*"
        headers["Origin"] = "https://prizes.gamee.com"
        headers["Sec-Fetch-Site"] = "cross-site"
        headers["Sec-Fetch-Mode"] = "cors"
        headers["Sec-Fetch-Dest"] = "empty"
        headers["Referer"] = "https://prizes.gamee.com/"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Accept-Language"] = "en-US,en;q=0.9"
        data = (
            '{"jsonrpc":"2.0","id":"user.authentication.botLogin","method":"user.authentication.botLogin","params":{"botName":"telegram","botGameUrl":"'
            + g
            + '","botUserIdentifier":null}}'
        )

        resp = requests.post(
        'http://api.service.gameeapp.com', 
        headers=headers, 
        data=data
        )
        result_data = resp.json()
        token = result_data["result"]["tokens"]["authenticate"]
        return token

    async def game_id(self, game_url):
        headers = CaseInsensitiveDict()
        headers["accept"] = "*/*"
        headers["accept-encoding"] = "gzip, deflate, br"
        headers["accept-language"] = "en-US,en;q=0.9"
        headers["cache-control"] = "no-cache"
        headers["client-language"] = "en"
        headers["content-length"] = "173"
        headers["Content-Type"] = "application/json"
        headers["origin"] = "https://prizes.gamee.com"
        headers["pragma"] = "no-cache"
        headers["referer"] = "https://prizes.gamee.com/"
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = "Windows"
        headers["sec-fetch-dest"] = "empty"
        headers["sec-fetch-mode"] = "cors"
        headers["sec-fetch-site"] = "cross-site"
        headers[
        "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        data = (
            '{"jsonrpc":"2.0","id":"game.getWebGameplayDetails","method":"game.getWebGameplayDetails","params":{"gameUrl":"'
            + game_url
            + '"}}'
        )

        resp = requests.post('https://api.service.gameeapp.com/', headers=headers, data=data)
        result_data = resp.json()
        return result_data["result"]["game"]["id"]

    async def send_score(self, score, timePlay, checksum, token, game_url, game_id):
        headers = CaseInsensitiveDict()
        headers["Host"] = "api.service.gameeapp.com"
        headers[
        "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/89.0.4389.90 Safari/537.36"
        headers["Accept"] = "*/*"
        headers["Accept-Language"] = "en-US,en;q=0.5"
        headers["Accept-Encoding"] = "gzip, deflate"
        headers["X-Install-Uuid"] = "91516df9-f651-40ef-9c11-ccd357429228"
        headers["Client-Language"] = "en"
        headers["Content-Type"] = "application/json"
        headers["Origin"] = "https://prizes.gamee.com"
        headers["Referer"] = "https://prizes.gamee.com/"
        headers["Sec-Fetch-Dest"] = "empty"
        headers["Sec-Fetch-Mode"] = "cors"
        headers["Sec-Fetch-Site"] = "cross-site"
        headers["Te"] = "trailers"
        headers["Authorization"] = "Bearer {my_token}".format(my_token=token)
        data = (
        '{"jsonrpc":"2.0","id":"game.saveWebGameplay","method":"game.saveWebGameplay","params":{"gameplayData":{"gameId":'
        + str(game_id)
        + ',"score":'
        + str(score)
        + ',"playTime":'
        + str(timePlay)
        + ',"gameUrl":"'
        + game_url
        + '","metadata":{"gameplayId":30},"releaseNumber":8,"gameStateData":null,"createdTime":"2021-12-28T03:20:24+03:30","checksum":"'
        + checksum
        + '","replayVariant":null,"replayData":null,"replayDataChecksum":null,"isSaveState":false,"gameplayOrigin":"game"}}}'
        )
        resp = requests.post("http://api.service.gameeapp.com", headers=headers, data=data)

        if resp.status_code == 200:
            for i in list(resp.json()):
                if i == "error":
                    my_json = resp.json()
                    logging.error(f"You are banned in @gamee on {my_json['user']['cheater']['banStatus']}")
                    return('ban')

        else:
            return True

class GameeCheatMod(loader.Module):
    """Читы для игр в @gamee"""
    
    strings = {
		"name": "GameeCheats",
		"result": (
			"<b>Рекорд накручен</b>!\n"
			"Новый рекорд: <code>{}</code>"
		),
		"err_args": (
			'<b>Введите нужные аргументы</b>!\n'
			'Пример: <code>{}chg <ссылка> <рекорд></code>'
		),
		"banned": (
			"<b>Вы были заблокированы в боте</b>!\n"
			"<code>Вы не можете ставить новые рекорды в течении 24 часов</code>"
		),
		"error_link": (
			"<b>Вы ввели неправильную ссылку</b>!\n"
			"<code>Введите правильную ссылку</code>"
			'Пример: .chg https://prizes.gamee.com/game-bot/karatekid2-... 123456</a>'
		)
	}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lib = GameCheatsLib()

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def chgcmd(self, message):
        """.chg <ссылка> <рекорд>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('err_args').format(self.get_prefix()))
            return

        try:
            game, score = args.split(' ')
        except:
            await utils.answer(message, self.strings('err_args').format(self.get_prefix()))
            return

        game_url = await self.game_link(game)
        if game_url == False:
            await utils.answer(message, self.strings('error_link'))
            return

        time = random.randint(308, 19187)
        checksum = await self.get_checksum(score, time, game_url)

        token = await self.lib.get_token(game_url)
        Game_number = await self.lib.game_id(game_url)
        result = await self.lib.send_score(score, time, checksum, token, game_url, Game_number)

        if result == 'ban':
            await utils.answer(message, self.strings('banned'))
            return

        await utils.answer(message, self.strings("result").format(score))

    async def game_link(self, url):
        pattern = r"https:\/\/prizes\.gamee\.com(\/game-bot\/.*)#tg"
        result = re.match(pattern, url)
        if result:
            return result.groups(0)[0]
        else:
            return False

    async def get_checksum(self, score, playTime, url):
        str2hash = f"{score}:{playTime}:{url}::crmjbjm3lczhlgnek9uaxz2l9svlfjw14npauhen"
        result = hashlib.md5(str2hash.encode())
        checksum = result.hexdigest()
        return checksum


def register(cb):
    cb(GameeCheatMod())