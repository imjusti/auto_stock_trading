# [2022-11-05] 자동매매 프로그램의 로그파일을 감시하며 텔레그램으로 상태를 알림

import os
import time
import datetime
import os.path
import telegram
import json
import os


# 로그파일 읽기
def loadLogFile(filename):
    with open(filename, 'rt', encoding='UTF-8') as f:
        arrLog = f.readlines()
    return arrLog

# 현재상태 구하기
def getStatus(strLine):
    status = None
    if strLine.find('Idle==================') > -1:
        status = strLine[-4:].strip()
    elif strLine.find('매수주문이 완료되었습니다.') > -1:
        status = 'buying'
    elif strLine.find('매도주문이 완료되었습니다.') > -1:
        status = 'Selling'
    return status

# 상태에 따른 메시지 생성
def getMessage(currStatus, status):
    strMessage = None
    # Sel로 상태 변경시
    if currStatus != 'Sel' and status == 'Sel':
        strMessage = '매수완료'
    # buying로 상태 변경시
    elif currStatus != 'buying' and status == 'buying':
        strMessage = '매수주문 완료'
    # Selling로 상태 변경시
    elif currStatus != 'Selling' and status == 'Selling':
        strMessage = '매도주문 완료'
    return strMessage


# 실행경로
path = os.path.dirname(os.path.realpath(__file__))

# 설정파일 읽기
with open(path + '/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 텔레그램 설정파일 읽기
with open(path + '/telegram.json') as f:
    cfg_telegram = json.load(f)
bot = telegram.Bot(token=cfg_telegram['token'])

currLine = 0
currStatus = 'buy'  # buy -> buying -> Sel -> Selling
currTime = 0
while True:
    # 오늘날짜
    dt_today = datetime.date.today()
    filename = config['log_path'] + '/Log' + dt_today.strftime('%Y-%m-%d') + '.dat'

    if os.path.isfile(filename):
        # 로그파일 읽어오기
        arrLog = loadLogFile(filename)
        last_line = arrLog[-1]
        print('last_line:' + last_line)

        # 로그파일 훑어보기
        print("currLine", currLine)
        if len(arrLog) > currLine:
            botMessage = ''
            for lineNumber in range(currLine, len(arrLog)):
                strLine = arrLog[lineNumber];
                currLine = lineNumber
                currTime = datetime.datetime.strptime(strLine[1:18], '%y-%m-%d %H:%M:%S')

                # 상태를 가져오고
                status = getStatus(strLine)
                # 상태에 따라 메시지를 만들고
                strMessage = getMessage(currStatus, status)
                # 출력할 메시지를 만들고
                if strMessage is not None: botMessage = botMessage + "\n" + strMessage
                # 최종상태를 갱신
                if status is not None: currStatus = status;

            if len(botMessage) > 0:
                bot.sendMessage(chat_id=cfg_telegram['chat_id'], text=botMessage)
                print(currTime, botMessage)
        print(currStatus)

        # 매도후에는 모니터링 종료
        if currStatus == 'Selling':
            break
        else:
            # 로그 출력시간 가져오기
            dtime = datetime.datetime.strptime(last_line[1:18], '%y-%m-%d %H:%M:%S')

            # 현재시간과의 차이 구하기(오래동안 갱신이 안되면 문제가 있다는 것)
            diff = datetime.datetime.now() - dtime;
            print(str(dtime) + ' diff:' + str(diff.seconds))
            errorSec = 120  # 120초 동안 로그 갱신이 안되면 에러
            if currStatus == 'buying': errorSec = 60 * 10  # 매수주문 후에는 10분까지 괜찮음
            if diff.seconds > errorSec:
                print('error! 로그 갱신 안됨')

                # 텔레그램으로 메시지 전송
                bot.sendMessage(chat_id=cfg_telegram['chat_id'], text='로그 갱신 오류')

                exit()

    time.sleep(30)
