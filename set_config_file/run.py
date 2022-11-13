# [221028] 자동매매 프로그램 설정파일 세팅

import requests
from bs4 import BeautifulSoup
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import json

path = 'C:/projects/python/auto_stock_trading/set_config_file/'

# 매수/매도시간
stime = "08:51"
etime = "10:01"
etime2 = "15:21"

# 설정파일 읽기
with open(path + "telegram.json") as f:
    config = json.load(f)

# 오늘날짜
dt_today = datetime.date.today()
str_today = dt_today.strftime('%Y-%m-%d')
print("\ndate: " + str_today)

# 조건8 예측정보 가져오기
url = "https://imjusti.cafe24.com/stock/calc_world_index.php"
req = requests.get(url)
soup = BeautifulSoup(req.content, 'html.parser')
result = soup.find(id="result")
case8 = result.string
print("조건8", case8)

# 조건1,7 예측정보 가져오기
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
json_file_name = path + "/google-docs-key.json"
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1clAW-k3iSO24vRqMm2KRBWxdY-F8vlkeLZFARE8FRno/edit#gid=1099702506"

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
doc = gc.open_by_url(spreadsheet_url)
worksheet = doc.worksheet("2018-10-31:종가시가관계")
cell = worksheet.find(str_today)
case1 = worksheet.acell('AA' + str(cell.row)).value
case7 = worksheet.acell('AQ' + str(cell.row)).value
print("조건1", case1)
print("조건7", case7)

# 오늘의 방향 결정
dirToday = -1
msg = "금일휴업"
if case8 == str(case1):
    dirToday = case1
    msg = "10시매도"
elif case8 == str(case7):
    dirToday = case7
    etime = etime2
    msg = "종가매도"

if dirToday > -1:
    msg += ", 방향: " + str(dirToday)
    
    # 매매할 종목
    stock_code = "122630"    # KODEX 레버리지
    if dirToday == "0": stock_code = "252710"    # TIGER 200선물인버스2X

    # 자동매매 프로그램 설정파일 생성
    f = open("C:\Release\Data\Strategy.json", 'w')
    f.write("{ \n")
    f.write("  \"time\": \"" + str_today + "\", \n")
    f.write("  \"timeBuy\": \"" + stime + "\", \n")
    f.write("  \"timeSel\": \"" + etime + "\", \n")
    f.write("  \"Code\": \"" + stock_code + "\", \n")
    f.write("  \"Deposit\": 0 \n")
    f.write("} \n")
    f.close()

print("[오늘의 작전] " + msg)

# 텔레그램으로 메시지 전송
bot = telegram.Bot(token=config['token'])
chat_id = config['chat_id']
bot.sendMessage(chat_id=chat_id, text="[오늘의 작전] " + msg)
