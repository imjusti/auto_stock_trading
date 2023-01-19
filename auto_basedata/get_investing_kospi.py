# 인베스팅닷컴의 코스피지수 기술적 분석값 긁어오기

import requests
import json
import os
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

# 실행경로
path = os.path.dirname(os.path.realpath(__file__))
# 설정파일 읽기
with open(path + '/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

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
html1 = soup.select('#techStudiesInnerWrap > div.summary > span')
str1 = html1[0].get_text()
print('요약:' + str1)
html2 = soup.select('#techStudiesInnerWrap > div:nth-child(2) > span.bold')
str2 = html2[0].get_text()
print('이동평균:' + str2)
html3 = soup.select('#techStudiesInnerWrap > div:nth-child(3) > span.bold')
str3 = html3[0].get_text()
print('기술지표:' + str3)

# 서버로 전송
val = str(txt2code(str1)) + ',' + str(txt2code(str2)) + ',' + str(txt2code(str3))
url = config['url_save_invesing_kospi'] + '&val=' + val
res = requests.get(url)
print(val, res)
