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
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    result = soup.find(id='result')
    return int(result.string)

# 조건1,5,7 예측정보 가져오기
def getCaseFromGSpread(worksheet, str_today, case1_colname, case5_colname, case7_colname):
    cell = worksheet.find(str_today)
    result = None
    if cell is not None:
        case1 = int(worksheet.acell(case1_colname + str(cell.row)).value)
        case5 = int(worksheet.acell(case5_colname + str(cell.row)).value)
        case7 = int(worksheet.acell(case7_colname + str(cell.row)).value)
        result = {'조건1': case1, '조건5': case5, '조건7': case7}
    return result

# 조건1,5,7 예측정보 가져오기
def getStrategy(url, str_today):
    res = requests.get(url + str_today)
    obj = res.json();
    case1 = int(obj['case1'])
    case5 = int(obj['case5'])
    case7 = int(obj['case7'])
    result = {'조건1': case1, '조건5': case5, '조건7': case7}
    return result

# 전략 결정
def decideStrategy(trading_type, cases):
    # 방향(0: 하락, 1: 상승, -1: 휴업)
    dirToday = -1
    # 매도시점(1: 10시, 2: 종가)
    sellType = 1

    # 조건1
    if trading_type == 1:
        dirToday = cases['조건1']
        sellType = 2
    # 조건5
    elif trading_type == 5:
        dirToday = cases['조건5']
        sellType = 2
    # 조건6
    elif trading_type == 6:
        if cases['조건5'] == cases['조건1']:
            dirToday = cases['조건1']
            sellType = 2
    # 조건7
    elif trading_type == 7:
        dirToday = cases['조건7']
        sellType = 2
    # 조건8
    elif trading_type == 8:
        dirToday = cases['조건8']
        sellType = 1
    # 조건9
    elif trading_type == 9:
        if cases['조건8'] == cases['조건1']:
            dirToday = cases['조건8']
            sellType = 1
    # 조건11
    elif trading_type == 11:
        if cases['조건8'] == cases['조건5']:
            dirToday = cases['조건8']
            sellType = 1

    return (dirToday, sellType)

# 전략파일 생성
def write2StrategyFile(str_today, buy_time, sell_time, stock_code, amount, file_path):
    data = {
        'time': str_today,
        'timeBuy': buy_time,
        'timeSel': sell_time,
        'Code': stock_code,
        'Deposit': amount
    }
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=2)
        
# 메시지 생성
def makeMessage(str_today, dirToday, sellType, cases, fundName):
    msg = '금일휴업'
    if dirToday > -1:
        if sellType == 1: msg = '10시매도'
        elif sellType == 2: msg = '종가매도'
        msg += ', 방향: ' + str(dirToday)

    msg_telegram = '** ' + fundName + ' **\n'
    msg_telegram += '날짜: ' + str_today+ '\n\n'
    msg_telegram += '[오늘의 작전]\n'
    msg_telegram += msg + '\n'
    msg_telegram += '\n'

    # 각 조건값들 전송
    msg_telegram += '[참고 조건값들]\n'
    msg_telegram += '조건1: ' + str(cases['조건1']) + '\n'
    msg_telegram += '조건5: ' + str(cases['조건5']) + '\n'
    msg_telegram += '조건7: ' + str(cases['조건7']) + '\n'
    msg_telegram += '조건8: ' + str(cases['조건8']) + '\n'
    msg_telegram += '\n'
    
    return msg_telegram

# 텔레그램 전송
def sendTelegramMsg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)
    print(msg)
