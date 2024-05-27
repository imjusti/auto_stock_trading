import requests
from bs4 import BeautifulSoup
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import json
import os


# 조건1,2,5,7,8,150,150x2,필터1 예측정보 가져오기
def getStrategy(url, str_today):
    res = requests.get(url + str_today)
    obj = res.json();

    case1 = ''
    case2 = ''
    case5 = ''
    case7 = ''
    case8 = ''
    range150 = ''
    range150x2 = ''
    filter1 = ''

    if obj['case1'] is not None: case1 = int(obj['case1'])
    if obj['case5'] is not None: case5 = int(obj['case5'])
    if obj['case7'] is not None: case7 = int(obj['case7'])
    if obj['case8'] is not None: case8 = int(obj['case8'])

    if obj['range150'] is not None: range150 = int(obj['range150'])
    if obj['range150x2'] is not None: range150x2 = int(obj['range150x2'])

    if obj['filter1'] is not None: filter1 = int(obj['filter1'])

    if obj['case2'] is not None: case2 = int(obj['case2'])
        
    result = {'조건1': case1, '조건2': case2, '조건5': case5, '조건7': case7, '조건8': case8, '범위150': range150, '범위150x2': range150x2, '필터1': filter1}
    return result

# 전략 결정
def decideStrategy(trading_type0, cases):
    result = trading_type0.split("_")
    trading_type = result[0] if result else ''
    trading_filter = result[1] if len(result) > 1 else ''
    
    # 방향(0: 하락, 1: 상승, -1: 휴업)
    dirToday = -1
    # 매도시점(1: 10시, 2: 종가)
    sellType = 2

    # 조건1
    if trading_type == '1': dirToday = cases['조건1']
    # 조건5
    elif trading_type == '5': dirToday = cases['조건5']
    # 조건6
    elif trading_type == '6':
        if cases['조건5'] == cases['조건1']:  dirToday = cases['조건1']
    # 조건7
    elif trading_type == '7': dirToday = cases['조건7']
    # 조건8
    elif trading_type == '8': dirToday = cases['조건8']
    # 조건9
    # 23.09.26 종가매도로 변경
    elif trading_type == '9':
        if cases['조건8'] == cases['조건2']: dirToday = cases['조건8']
    # 조건11
    elif trading_type == '11':
        if cases['조건8'] == cases['조건5']: dirToday = cases['조건8']
    # 조건12
    elif trading_type == '12':
        if cases['조건8'] == cases['조건5']: dirToday = cases['조건8']
        elif cases['조건8'] == cases['조건2']: dirToday = cases['조건8']

    # 필터 확인
    if trading_filter and cases['필터' + trading_filter] != 1: dirToday = -1

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
    msg_telegram += '조건2: ' + str(cases['조건2']) + '\n'
    msg_telegram += '조건5: ' + str(cases['조건5']) + '\n'
    msg_telegram += '조건7: ' + str(cases['조건7']) + '\n'
    msg_telegram += '조건8: ' + str(cases['조건8']) + '\n'
    msg_telegram += '필터1: ' + str(cases['필터1']) + '\n'
    msg_telegram += '범위150: ' + str(cases['범위150']) + '\n'
    msg_telegram += '범위150x2: ' + str(cases['범위150x2']) + '\n'
    msg_telegram += '\n'
    
    return msg_telegram

# 텔레그램 전송
def sendTelegramMsg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)
    print(msg)
