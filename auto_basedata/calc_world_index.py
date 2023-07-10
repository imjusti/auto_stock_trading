import requests
import json
import os
import telegram
import asyncio

# 텔레그램 전송
async def sendTelegramMsg(fundName, bot, chat_id, msg):
    last_msg = '** ' + fundName + ' **\n'
    last_msg += msg
    await bot.sendMessage(chat_id=chat_id, text=last_msg)
    print(last_msg)


# 실행경로
path = os.path.dirname(os.path.realpath(__file__))

# 설정파일 읽기
with open(path + '/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 텔레그램 설정파일 읽기
with open(path + '/telegram.json') as f:
    cfg_telegram = json.load(f)
bot = telegram.Bot(token=cfg_telegram['token'])

res = requests.get(config['url_calc_world_index'])
print(config['url_calc_world_index'], res.text)

# 텔레그램으로 메시지 전송
asyncio.run(sendTelegramMsg('해외지수', bot, cfg_telegram['chat_id'], res.text))
