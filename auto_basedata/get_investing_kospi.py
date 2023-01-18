# 인베스팅닷컴의 코스피지수 기술적 분석값 긁어오기

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep

driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.get('https://kr.investing.com/indices/kospi-technical')
sleep(3);
driver.find_element(By.XPATH, '//*[@id="timePeriodsWidget"]/li[6]/a').click()
sleep(2)
html = driver.page_source

soup = BeautifulSoup(html, 'html.parser')
html1 = soup.select('#techStudiesInnerWrap > div.summary > span')
print(html1[0].get_text())
html2 = soup.select('#techStudiesInnerWrap > div:nth-child(2) > span.bold')
print(html2[0].get_text())
html3 = soup.select('#techStudiesInnerWrap > div:nth-child(3) > span.bold')
print(html3[0].get_text())
