# 인베스팅닷컴의 코스피지수 기술적 분석값 긁어오기

import requests
import json
import os
import telegram
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep

def txt2code(txt):
    code = 0

    txt = txt.lower()

    # 방향 확인
    if 'buy' in txt: code = 1;
    elif 'sell' in txt: code = -1;

    # 강도 확인
    if 'strong' in txt: code = code * 2;

    return str(code)

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


# 크롬으로 페이지 긁어오기
driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()))
driver.implicitly_wait(5)

# 1시간 자료
arr_1hour = getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/37426/1h')
# 5시간 자료
arr_5hour = getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/37426/5h')
# 일간 자료
arr_day = getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/37426/1d')
# 주간 자료
arr_week = getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/37426/1w')
# 월간 자료
arr_month = getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/37426/1mo')

driver.quit()

val_1hour = ','.join(arr_1hour)
print(val_1hour)


