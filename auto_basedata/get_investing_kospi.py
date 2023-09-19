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

    if txt == '매수': code = 1
    elif txt == '적극 매수': code = 2
    elif txt == '매도': code = -1
    elif txt == '적극 매도': code = -2
    return code

def getCodes(driver, selector):
    # 자료 클릭
    driver.find_element(By.CSS_SELECTOR, selector).click()
    sleep(3)
    html = driver.page_source
    # 페이지 파싱
    soup = BeautifulSoup(html, 'html.parser')

    str = soup.select('div[data-test="timeframe-selection"] > div:nth-child(2) > div > div')[0].get_text()
    
    pos1 = str.find('요약')
    str0 = str[pos1 + 2 + 16:pos1 + 2 + 30]
    str1 = str0[0:str0.find('매수:')]
    print('요약:' + str1)

    pos1 = str.find('이동평균')
    str0 = str[pos1 + 4 + 16:pos1 + 4 + 30]
    str2 = str0[0:str0.find('매수:')]
    print('이동평균:' + str2)

    pos1 = str.find('기술적 지표')
    str0 = str[pos1 + 6 + 16:pos1 + 6 + 30]
    str3 = str0[0:str0.find('매수:')]
    print('기술지표:' + str3)
    
    return [str1, str2, str3]

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
driver.get('https://kr.investing.com/indices/kospi-technical')
sleep(3);
driver.execute_script("window.scrollTo(0, 700)")
sleep(3);

# 5분자료
arr_5min = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(1)')
# 15분자료
arr_15min = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(2)')
# 30분자료
arr_30min = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(3)')
# 1시간자료
arr_1hour = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(4)')
# 5시간자료
arr_5hour = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(5)')
# 일간자료
arr_day = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(6)')
# 주간자료
arr_week = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(7)')
# 월간자료
arr_month = getCodes(driver, 'div[data-test="timeframe-selection"] .inv-tab-bar button:nth-child(8)')

driver.quit()

# 서버로 전송
val_5min = str(txt2code(arr_5min[0])) + ',' + str(txt2code(arr_5min[1])) + ',' + str(txt2code(arr_5min[2]))
val_15min = str(txt2code(arr_15min[0])) + ',' + str(txt2code(arr_15min[1])) + ',' + str(txt2code(arr_15min[2]))
val_30min = str(txt2code(arr_30min[0])) + ',' + str(txt2code(arr_30min[1])) + ',' + str(txt2code(arr_30min[2]))
val_1hour = str(txt2code(arr_1hour[0])) + ',' + str(txt2code(arr_1hour[1])) + ',' + str(txt2code(arr_1hour[2]))
val_5hour = str(txt2code(arr_5hour[0])) + ',' + str(txt2code(arr_5hour[1])) + ',' + str(txt2code(arr_5hour[2]))
val_day = str(txt2code(arr_day[0])) + ',' + str(txt2code(arr_day[1])) + ',' + str(txt2code(arr_day[2]))
val_week = str(txt2code(arr_week[0])) + ',' + str(txt2code(arr_week[1])) + ',' + str(txt2code(arr_week[2]))
val_month = str(txt2code(arr_month[0])) + ',' + str(txt2code(arr_month[1])) + ',' + str(txt2code(arr_month[2]))
url = config['url_save_invesing_kospi'] + '&'.join(['', '5min_val=' + val_5min, '15min_val=' + val_15min, '30min_val=' + val_30min, '1hour_val=' + val_1hour, '5hour_val=' + val_5hour, 'day_val=' + val_day, 'week_val=' + val_week, 'month_val=' + val_month])
res = requests.get(url)
print(url, res.text)

# 텔레그램으로 메시지 전송
msg = '\n'.join(['5분: ' + val_5min, '15분: ' + val_15min, '30분: ' + val_30min, '1시간: ' + val_1hour, '5시간: ' + val_5hour, '일간: ' + val_day, '주간: ' + val_week, '월간: ' + val_month, 'result: ' + res.text])
asyncio.run(sendTelegramMsg('조건90', bot, cfg_telegram['chat_id'], msg))
