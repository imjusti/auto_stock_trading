# [221028] 자동매매 프로그램 설정파일 세팅

import datetime
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


# 조건1,5,7 예측정보 가져오기
cases = lib.getStrategy(config['strategy_url'], str_today)
# 조건8 예측정보 가져오기
cases['조건8'] = lib.getCase8(config['case8_url'])
print(cases)

# 오늘의 방향 결정
dirToday, sellType = lib.decideStrategy(config['trading_type'], cases)

if dirToday > -1:
    etime = config['sell_time']
    if sellType == 2: etime = config['sell_time2']
    
    # 매매할 종목
    stock_code = config['case1_stock_code']
    if dirToday == 0: stock_code = config['case0_stock_code']

    lib.write2StrategyFile(str_today, config['buy_time'], etime, stock_code, config['trading_amount'], config['output_path'])

# 텔레그램으로 오늘의 작전 전송
msg_telegram = lib.makeMessage(str_today, dirToday, sellType, cases, config['name'])
lib.sendTelegramMsg(bot, cfg_telegram['chat_id'], msg_telegram)
