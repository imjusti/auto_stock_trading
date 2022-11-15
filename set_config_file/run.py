# [221028] 자동매매 프로그램 설정파일 세팅

import requests
from bs4 import BeautifulSoup
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import json
import os

# 실행경로
path = os.path.dirname(os.path.realpath(__file__))

# 설정파일 읽기
with open(path + "/config.json", 'r', encoding='utf-8') as f:
    config = json.load(f)
    
# 텔레그램 설정파일 읽기
with open(path + "/telegram.json") as f:
    cfg_telegram = json.load(f)
bot = telegram.Bot(token=cfg_telegram['token'])
chat_id = cfg_telegram['chat_id']

# 매수/매도시간
stime = config['buy_time']
etime = config['sell_time']
etime2 = config['sell_time2']
# 설정파일 경로
output_path = config['output_path']

# 오늘날짜
dt_today = datetime.date.today()
str_today = dt_today.strftime('%Y-%m-%d')
print("\ndate: " + str_today)

# 조건8 예측정보 가져오기
url = config['case8_url']
req = requests.get(url)
soup = BeautifulSoup(req.content, 'html.parser')
result = soup.find(id="result")
case8 = int(result.string)
print("조건8", case8)

# 조건1,7 예측정보 가져오기
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
json_file_name = path + "/google-docs-key.json"
spreadsheet_url = config['google_spreadsheet_url']

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
doc = gc.open_by_url(spreadsheet_url)
worksheet = doc.worksheet(config['google_spreadsheet_worksheet'])
cell = worksheet.find(str_today)
case1 = int(worksheet.acell(config['google_spreadsheet_case1_colname'] + str(cell.row)).value)
case7 = int(worksheet.acell(config['google_spreadsheet_case7_colname'] + str(cell.row)).value)
print("조건1", case1)
print("조건7", case7)

# 오늘의 방향 결정
dirToday = -1
msg = "금일휴업"
if case8 == case1:
    dirToday = case1
    msg = "10시매도"
elif case8 == case7:
    dirToday = case7
    etime = etime2
    msg = "종가매도"

if dirToday > -1:
    msg += ", 방향: " + str(dirToday)
    
    # 매매할 종목
    stock_code = "122630"    # KODEX 레버리지
    if dirToday == "0": stock_code = "252710"    # TIGER 200선물인버스2X

    # 자동매매 프로그램 설정파일 생성
    data = {
        'time': str_today,
        'timeBuy': stime,
        'timeSel': etime,
        'Code': stock_code,
        'Deposit': 0
    }
    with open(output_path, 'w') as outfile:
        json.dump(data, outfile, indent=2)

# 텔레그램으로 오늘의 작전 전송
msg_telegram = "[오늘의 작전] " + msg
bot.sendMessage(chat_id=chat_id, text=msg_telegram)
print(msg_telegram)

# 각 조건값들 전송
msg_telegram = '조건1: ' + str(case1) + '\n'
msg_telegram += '조건7: ' + str(case7) + '\n'
msg_telegram += '조건8: ' + str(case8) + '\n'
bot.sendMessage(chat_id=chat_id, text=msg_telegram)

## 추가정보
# 최근 적중율
case8_hit = worksheet.acell('BG' + str(cell.row - 1)).value
case9_hit = worksheet.acell('BL' + str(cell.row - 1)).value
case10_hit = worksheet.acell('BQ' + str(cell.row - 1)).value
# MDD
case8_mdd = worksheet.acell('BF' + str(cell.row + 6)).value
case9_mdd = worksheet.acell('BK' + str(cell.row + 6)).value
case10_mdd = worksheet.acell('BP' + str(cell.row + 6)).value
msg_telegram = '[최근적중율, MDD]\n'
msg_telegram += '조건8: ' + str(case8_hit) + '%, ' + str(case8_mdd) + '\n'
msg_telegram += '조건9: ' + str(case9_hit) + '%, ' + str(case9_mdd) + '\n'
msg_telegram += '조건10: ' + str(case10_hit) + '%, ' + str(case10_mdd)
bot.sendMessage(chat_id=chat_id, text=msg_telegram)
print(msg_telegram)
