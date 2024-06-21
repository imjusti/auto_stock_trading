import telegram
from bs4 import BeautifulSoup
import json
import asyncio


def txt2code(txt):
    code = 0

    txt = txt.lower()

    # 방향 확인
    if 'buy' in txt: code = 1
    elif 'sell' in txt: code = -1

    # 강도 확인
    if 'strong' in txt: code = code * 2

    return str(code)

# 요약정보 가져오기
def getCodes(driver, url):
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('body')

    code_summary = -99
    code_moving = -99
    code_indicator = -99
    try:
        json_data = json.loads(body.pre.text)

        code_summary = txt2code(json_data["summary"])
        code_moving = txt2code(json_data["movingAverages"]["summary"]["value"])
        code_indicator = txt2code(json_data["indicators"]["summary"]["value"])
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return [code_summary, code_moving, code_indicator]


# 기술지표 가져오기
def getIndicators(driver, url):
    driver.get(url)
	
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('body')

    indicators = []
    try:
        json_data = json.loads(body.pre.text)

        for key in json_data["indicators"]:
            indicator = json_data["indicators"][key]
            if "action" in indicator:
                value = indicator["value"]
                action = indicator["action"]
                indicators.append(f"{key}:{value}:{action}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return indicators

# 텔레그램 전송
async def sendTelegramMsg(fundName, bot, chat_id, msg):
    last_msg = '** ' + fundName + ' **\n'
    last_msg += msg
    await bot.sendMessage(chat_id=chat_id, text=last_msg)
    print(last_msg)
