# [221028] 자동매매 프로그램 설정파일 세팅

import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import json
import os
import lib

# 실행경로
path = os.path.dirname(os.path.realpath(__file__))
# 설정파일 읽기
with open(path + '/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 텔레그램 설정파일 읽기
with open(path + "/telegram.json") as f:
    cfg_telegram = json.load(f)
bot = telegram.Bot(token=cfg_telegram['token'])
# 오늘날짜
str_today = datetime.date.today().strftime('%Y-%m-%d')
print('\ndate: ' + str_today)


# 조건8 예측정보 가져오기
case8 = lib.getCase8(config['case8_url'])
print('조건8', case8)

# 조건1,5,7 예측정보 가져오기
worksheet = lib.getGSpread(config['google_spreadsheet_url'], config['google_spreadsheet_worksheet'])
result = lib.getCaseFromGSpread(worksheet, str_today, config['google_spreadsheet_case1_colname'], config['google_spreadsheet_case5_colname'], config['google_spreadsheet_case7_colname'])
if result is None:
    lib.sendTelegramMsg(bot, cfg_telegram['chat_id'], '[오류] 엑셀에서 ' + str_today + ' 데이터를 가져오지 못했습니다.')
    exit()
case1, case5, case7 = result
print('조건1', case1)
print('조건5', case5)
print('조건7', case7)

# 오늘의 방향 결정
dirToday, sellType = lib.decideStrategy(case1, case5, case7, case8)

if dirToday > -1:
    etime = config['sell_time']
    if sellType == 2: etime = config['sell_time2']
    
    # 매매할 종목
    stock_code = '122630'    # KODEX 레버리지
    if dirToday == 0: stock_code = '252710'    # TIGER 200선물인버스2X

    lib.write2StrategyFile(str_today, config['buy_time'], etime, stock_code, config['output_path'])

# 텔레그램으로 오늘의 작전 전송
msg_telegram = lib.makeMessage(str_today, dirToday, sellType, case1, case5, case7, case8, worksheet)
lib.sendTelegramMsg(bot, cfg_telegram['chat_id'], msg_telegram)
