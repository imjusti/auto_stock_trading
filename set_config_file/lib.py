import requests
from bs4 import BeautifulSoup
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import json
import os


# 구글 스프레드시트 가져오기
def getGSpread(url, worksheet_name):
    path = os.path.dirname(os.path.realpath(__file__))
    
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path + '/google-docs-key.json', scope)
    gc = gspread.authorize(credentials)
    doc = gc.open_by_url(url)
    worksheet = doc.worksheet(worksheet_name)
    
    return worksheet

# 조건8 예측정보 가져오기
def getCase8(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    result = soup.find(id='result')
    return int(result.string)

# 조건1,7 예측정보 가져오기
def getCaseFromGSpread(worksheet, str_today, case1_colname, case7_colname):
    cell = worksheet.find(str_today)
    result = None
    if cell is not None:
        case1 = int(worksheet.acell(case1_colname + str(cell.row)).value)
        case7 = int(worksheet.acell(case7_colname + str(cell.row)).value)
        result = (case1, case7)
    return result

# 전략 결정
def decideStrategy(case1, case7, case8):
    dirToday = -1
    sellType = 1

    if case8 == case1:
        dirToday = case1
    elif case8 == case7:
        dirToday = case7
        sellType = 2

    return (dirToday, sellType)

# 전략파일 생성
def write2StrategyFile(str_today, buy_time, sell_time, stock_code, file_path):
    data = {
        'time': str_today,
        'timeBuy': buy_time,
        'timeSel': sell_time,
        'Code': stock_code,
        'Deposit': 0
    }
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=2)
        
# 메시지 생성
def makeMessage(str_today, dirToday, sellType, case1, case7, case8, worksheet):
    msg = '금일휴업'
    if dirToday > -1:
        if sellType == 1: msg = '10시매도'
        elif sellType == 2: msg = '종가매도'
        msg += ', 방향: ' + str(dirToday)

    msg_telegram = '날짜: ' + str_today+ '\n'
    msg_telegram += '[오늘의 작전] ' + msg + '\n'
    msg_telegram += '\n'

    # 각 조건값들 전송
    msg_telegram += '[참고 조건값들]\n'
    msg_telegram += '조건1: ' + str(case1) + '\n'
    msg_telegram += '조건7: ' + str(case7) + '\n'
    msg_telegram += '조건8: ' + str(case8) + '\n'
    msg_telegram += '\n'

    ## 추가정보
    cell = worksheet.find(str_today) 
    if cell is not None:
        # 최근 적중율
        case8_hit = worksheet.acell('BJ' + str(cell.row - 1)).value
        case9_hit = worksheet.acell('BO' + str(cell.row - 1)).value
        case10_hit = worksheet.acell('BT' + str(cell.row - 1)).value
        # MDD
        case8_mdd = worksheet.acell('BI' + str(cell.row + 6)).value
        case9_mdd = worksheet.acell('BN' + str(cell.row + 6)).value
        case10_mdd = worksheet.acell('BS' + str(cell.row + 6)).value
        msg_telegram += '[최근적중율, MDD]\n'
        msg_telegram += '조건8: ' + str(case8_hit) + '%, ' + str(case8_mdd) + '\n'
        msg_telegram += '조건9: ' + str(case9_hit) + '%, ' + str(case9_mdd) + '\n'
        msg_telegram += '조건10: ' + str(case10_hit) + '%, ' + str(case10_mdd)
    
    return msg_telegram

# 텔레그램 전송
def sendTelegramMsg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)
    print(msg)
