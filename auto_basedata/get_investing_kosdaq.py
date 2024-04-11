# 인베스팅닷컴의 코스닥지수 기술적 분석값 긁어오기

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
import lib


# 실행경로
path = os.path.dirname(os.path.realpath(__file__))

# 설정파일 읽기
with open(path + '/config.json', 'r', encoding='utf-8') as f: config = json.load(f)

# 텔레그램 설정파일 읽기
with open(path + '/telegram.json') as f: cfg_telegram = json.load(f)
bot = telegram.Bot(token=cfg_telegram['token'])

# 크롬으로 페이지 긁어오기
driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()))
driver.implicitly_wait(5)

# 5분 자료
arr_5min = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/5m')
# 15분 자료
arr_15min = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/15m')
# 30분 자료
arr_30min = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/30m')
# 1시간 자료
arr_1hour = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/1h')
# 5시간 자료
arr_5hour = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/5h')
# 일간 자료
arr_day = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/1d')
# 주간 자료
arr_week = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/1w')
# 월간 자료
arr_month = lib.getCodes(driver, 'https://api.investing.com/api/financialdata/technical/analysis/38016/1mo')

driver.quit()

# 서버로 전송
url = config['url_save_invesing_kosdaq'] + '&'.join([
    '',
    '5min_val=' + ','.join(arr_5min),
    '15min_val=' + ','.join(arr_15min),
    '30min_val=' + ','.join(arr_30min),
    '1hour_val=' + ','.join(arr_1hour),
    '5hour_val=' + ','.join(arr_5hour),
    'day_val=' + ','.join(arr_day),
    'week_val=' + ','.join(arr_week),
    'month_val=' + ','.join(arr_month)
])
res = requests.get(url)
print(url, res.text)

# 텔레그램으로 메시지 전송
msg = '\n'.join([
    '순서: 요약,이동,기술',
    '5분: ' + ','.join(arr_5min),
    '15분: ' + ','.join(arr_15min),
    '30분: ' + ','.join(arr_30min),
    '1시간: ' + ','.join(arr_1hour),
    '5시간: ' + ','.join(arr_5hour),
    '일간: ' + ','.join(arr_day),
    '주간: ' + ','.join(arr_week),
    '월간: ' + ','.join(arr_month),
    'result: ' + res.text
])
# 포지션 변경시 알림 표시
if res.text == '1' or res.text == '0': msg = msg + '\n\n!! 새 포지션 !! ' + res.text
asyncio.run(lib.sendTelegramMsg('조건90(KOSDAQ)', bot, cfg_telegram['chat_id'], msg))

