# 인베스팅닷컴의 코스피지수 기술적 분석값 긁어오기

import requests
import json
import os
import telegram
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep

def txt2code(txt):
    code = 0

    if txt == '매수': code = 1
    elif txt == '적극 매수': code = 2
    elif txt == '매도': code = -1
    elif txt == '적극 매도': code = -2

    return code

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
driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.get('https://kr.investing.com/indices/kospi-technical')
sleep(3);

# 일간자료 클릭
driver.find_element(By.XPATH, '//*[@id="timePeriodsWidget"]/li[6]/a').click()
sleep(1)
html = driver.page_source
# 페이지 파싱
soup = BeautifulSoup(html, 'html.parser')
day_str1 = soup.select('#techStudiesInnerWrap > div.summary > span')[0].get_text()
print('요약:' + day_str1)
day_str2 = soup.select('#techStudiesInnerWrap > div:nth-child(2) > span.bold')[0].get_text()
print('이동평균:' + day_str2)
day_str3 = soup.select('#techStudiesInnerWrap > div:nth-child(3) > span.bold')[0].get_text()
print('기술지표:' + day_str3)

# 주간자료 클릭
driver.find_element(By.XPATH, '//*[@id="timePeriodsWidget"]/li[7]/a').click()
sleep(1)
html = driver.page_source
# 페이지 파싱
soup = BeautifulSoup(html, 'html.parser')
week_str1 = soup.select('#techStudiesInnerWrap > div.summary > span')[0].get_text()
print('요약:' + week_str1)
week_str2 = soup.select('#techStudiesInnerWrap > div:nth-child(2) > span.bold')[0].get_text()
print('이동평균:' + week_str2)
week_str3 = soup.select('#techStudiesInnerWrap > div:nth-child(3) > span.bold')[0].get_text()
print('기술지표:' + week_str3)

# 월간자료 클릭
driver.find_element(By.XPATH, '//*[@id="timePeriodsWidget"]/li[8]/a').click()
sleep(1)
html = driver.page_source
# 페이지 파싱
soup = BeautifulSoup(html, 'html.parser')
month_str1 = soup.select('#techStudiesInnerWrap > div.summary > span')[0].get_text()
print('요약:' + month_str1)
month_str2 = soup.select('#techStudiesInnerWrap > div:nth-child(2) > span.bold')[0].get_text()
print('이동평균:' + month_str2)
month_str3 = soup.select('#techStudiesInnerWrap > div:nth-child(3) > span.bold')[0].get_text()
print('기술지표:' + month_str3)

# 서버로 전송
day_val = str(txt2code(day_str1)) + ',' + str(txt2code(day_str2)) + ',' + str(txt2code(day_str3))
week_val = str(txt2code(week_str1)) + ',' + str(txt2code(week_str2)) + ',' + str(txt2code(week_str3))
month_val = str(txt2code(month_str1)) + ',' + str(txt2code(month_str2)) + ',' + str(txt2code(month_str3))
url = config['url_save_invesing_kospi'] + '&day_val=' + day_val + '&week_val=' + week_val + '&month_val=' + month_val
res = requests.get(url)
print(day_val, res.text)

# 텔레그램으로 메시지 전송
msg = '일간: ' + day_val + '\n' + '주간: ' + week_val + '\n' + '월간: ' + month_val + '\nresult: ' + res.text
asyncio.run(sendTelegramMsg('조건90', bot, cfg_telegram['chat_id'], msg))
