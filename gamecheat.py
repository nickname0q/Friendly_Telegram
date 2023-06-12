import random, hashlib, re, requests, logging
from requests.structures import CaseInsensitiveDict
from telethon import events
from .. import loader, utils

class GameCheatsLib:
    TOKEN_URL = "http://api.service.gameeapp.com"
    GAME_DETAILS_URL = "https://api.service.gameeapp.com/"

    async def get_token(self, g):
        headers = CaseInsensitiveDict({
            "Host": "api.service.gameeapp.com",
            "Connection": "keep-alive",
            "Content-Length": "224",
            "client-language": "en",
            "x-install-uuid": "0c1cd354-302a-4e76-9745-6d2d3dcf2c56",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "sec-ch-ua-platform": "Windows",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://prizes.gamee.com",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://prizes.gamee.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        })

        data = {
            "jsonrpc": "2.0",
            "id": "user.authentication.botLogin",
            "method": "user.authentication.botLogin",
            "params": {
                "botName": "telegram",
                "botGameUrl": g,
                "botUserIdentifier": None
            }
        }

        resp = requests.post(self.TOKEN_URL, headers=headers, json=data)
        result_data = resp.json()
        token = result_data["result"]["tokens"]["authenticate"]
        return token

    async def game_id(self, game_url):
        headers = CaseInsensitiveDict({
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "client-language": "en",
            "content-length": "173",
            "Content-Type": "application/json",
            "origin": "https://prizes.gamee.com",
            "pragma": "no-cache",
            "referer": "https://prizes.gamee.com/",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        })

        data = {
            "jsonrpc": "2.0",
            "id": "game.getWebGameplayDetails",
            "method": "game.getWebGameplayDetails",
            "params": {
                "gameUrl": game_url
            }
        }

        resp = requests.post(self.GAME_DETAILS_URL, headers=headers, json=data)
        result_data = resp.json()
        return result_data["result"]["game"]["id"]

    async def send_score(self, score, time_play, checksum, token, game_url, game_id):
        headers = CaseInsensitiveDict({
            "Host": "api.service.gameeapp.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/89.0.4389.90 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "X-Install-Uuid": "91516df9-f651-40ef-9c11-ccd357429228",
            "Client-Language": "en",
            "Content-Type": "application/json",
            "Origin": "https://prizes.gamee.com",
            "Referer": "https://prizes.gamee.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Te": "trailers",
            "Authorization": f"Bearer {token}"
        })

        data = {
            "jsonrpc": "2.0",
            "id": "game.saveWebGameplay",
            "method": "game.saveWebGameplay",
            "params": {
                "gameplayData": {
                    "gameId": game_id,
                    "score": int(score),
                    "playTime": time_play,
                    "gameUrl": game_url,
                    "metadata": {
                        "gameplayId": 30
                    },
                    "releaseNumber": 8,
                    "gameStateData": None,
                    "createdTime": "2021-12-28T03:20:24+03:30",
                    "checksum": checksum,
                    "replayVariant": None,
                    "replayData": None,
                    "replayDataChecksum": None,
                    "isSaveState": False,
                    "gameplayOrigin": "game"
                }
            }
        }

        resp = requests.post(self.TOKEN_URL, headers=headers, json=data)

        if resp.status_code == 200:
            for i in resp.json().keys():
                if i == "error":
                    my_json = resp.json()
                    logging.error(f"Ошибка: {my_json}")
                    return 'error'

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
            "<b>Введите нужные аргументы</b>!\n"
            "Пример: <code>.chg <ссылка> <рекорд (в цифрах)></code>"
        ),
        "errored": (
            "<b>Ошибка. Чекай логи (.logs 40)</b>!"
        ),
        "error_link": (
            "<b>Вы ввели неправильную ссылку</b>!\n"
            "<code>Введите правильную ссылку</code>\n"
            "Пример: .chg https://prizes.gamee.com/game-bot/karatekid2-... 123456</a>"
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
            await utils.answer(message, self.strings['err_args'])
            return

        try:
            game, score = args.split(' ')
            if not score.isdigit():
                raise ValueError
        except:
            await utils.answer(message, self.strings['err_args'])
            return

        game_url = await self.game_link(game)
        if game_url == False:
            await utils.answer(message, self.strings['error_link'])
            return

        time_play = random.randint(308, 19187)
        checksum = await self.get_checksum(score, time_play, game_url)

        token = await self.lib.get_token(game_url)
        game_number = await self.lib.game_id(game_url)
        result = await self.lib.send_score(score, time_play, checksum, token, game_url, game_number)

        if result == 'error':
            await utils.answer(message, self.strings['errored'])
            return

        await utils.answer(message, self.strings["result"].format(score))

    async def game_link(self, url):
        pattern = r"https:\/\/prizes\.gamee\.com(\/game-bot\/.*)#tg"
        result = re.match(pattern, url)
        if result:
            return result.group(1)
        else:
            return False

    async def get_checksum(self, score, play_time, url):
        str2hash = f"{score}:{play_time}:{url}::crmjbjm3lczhlgnek9uaxz2l9svlfjw14npauhen"
        result = hashlib.md5(str2hash.encode())
        checksum = result.hexdigest()
        return checksum


def register(cb):
    cb(GameeCheatMod())
