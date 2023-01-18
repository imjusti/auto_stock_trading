import requests
import json
import os


# 실행경로
path = os.path.dirname(os.path.realpath(__file__))
# 설정파일 읽기
with open(path + '/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

req = requests.get(config['url'])
print(config['url'], req)
