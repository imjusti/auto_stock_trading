# [2022-11-05] 자동매매 프로그램의 로그파일을 감시하며 텔레그램으로 상태를 알림

import os
import time
import datetime
import os.path
import telegram
import json
import os

# 파일경로
path = os.path.dirname(os.path.realpath(__file__))

# 설정파일 읽기
with open(path + '/telegram.json') as f:
    config = json.load(f)

while(True):
    # 오늘날짜
    dt_today = datetime.date.today()
    filename = "C:\Release\Data\Log" + dt_today.strftime('%Y-%m-%d') + ".dat"

    if os.path.isfile(filename):
        # 마지막줄 읽어오기
        with open(filename, 'rt', encoding='UTF-8') as f:
            last_line = f.readlines()[-1]
        print("last_line:" + last_line)

        # 로그 출력시간 가져오기
        dtime = datetime.datetime.strptime(last_line[1:18], "%y-%m-%d %H:%M:%S")

        # 현재시간과의 차이 구하기(오래동안 갱신이 안되면 문제가 있다는 것)
        diff = datetime.datetime.now() - dtime;
        print(str(dtime) + " diff:" + str(diff.seconds))
        if (diff.seconds > 120):
            print("error! 로그 갱신 안됨")

            # 텔레그램으로 메시지 전송
            bot = telegram.Bot(token=config['token'])
            chat_id = config['chat_id']
            bot.sendMessage(chat_id=chat_id, text="로그 갱신 오류")
            time.sleep(60 * 5)

    time.sleep(30)
