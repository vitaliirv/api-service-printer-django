import base64
import json
import os
import random
from time import sleep

import pdfplumber
import redis
import requests
HOST = 'http://127.0.0.1:8000'
a = 56
with redis.Redis() as client:
    print(client.lrange('param_for_tasks', 0, -1))
    print(client.lrange('checks_id', 0, -1))
    # client.delete('checks_id')
    # client.hdel('check', 'id')
    # client.hdel(10,'qwert')
    # print(client.hget('check', 'id'))
    # print(client.hget(18, 'check_obj'))
    # print(client.hget(18, 'check_type'))
    # print(client.hget(10, 'id'))
    # # while True:
    #
    #     task = "{'check_obj': 100, 'ch_type': 200}"
    #     #random.randint(1, 100)
    #     print(task)
    #     sleep(random.randint(1, 2))
    #     client.lpush('tasks', task)
    #
    #     answer = client.brpop('answers')[1].decode('utf-8')
    #     print(f'Answer: {answer}')
p = f'{os.getcwd()}..media/pdf/17_kitchen.pdf'
# print(p)
url_check = 'http://127.0.0.1:8000/api/v1/check/56'
# check = requests.get(url_check).content.decode('utf-8')
# check = json.loads(check)
# print(check)
# print(check['id'], check['check_type'], check['order']['id'])

url = "http://127.0.0.1:8000/api/v1/check/86/"
# url = "http://127.0.0.1:8000/api/v1/update_check/check_id=87"
path = f'{HOST}/media/pdf/17_kitchen.pdf'
# pdf_file = requests.get(f'{HOST}/media/pdf/17_kitchen.pdf').text
# pdf_file = base64.b64encode(bytes(pdf_file, 'utf-8')).decode('utf-8')
# print(pdf_file)
# with pdfplumber.open(pdf_file) as temp:
#     file = temp
# print(file)

# files = {'17_kitchen.pdf': open('/home/brother/Python_Projects/Restaurant/restaurant/media/pdf/17_kitchen.pdf', 'rb')}
#
# r = requests.put(url, files=files)

# data = {'pdf_path': 'media/pdf/17_kitchen.pdf', 'status': 'rendered'}
# files = [{'file': (path, file)}]
# with open('/home/brother/Python_Projects/Restaurant/restaurant/media/pdf/17_kitchen.pdf', 'rb') as file:
# files = {'17_kitchen.pdf': pdf_file}
# file = open('/home/brother/Python_Projects/Restaurant/restaurant/media/pdf/17_client.pdf', 'rb')
#
# files = {'pdf_file': (f'18_test.pdf', file)}
#
# response = requests.put(url, data=data, files=files)
#
# print(response.text)

