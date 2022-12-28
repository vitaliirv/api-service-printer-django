import json

import asyncio
import os

import redis
import requests
import base64

from asgiref.sync import sync_to_async

HOST = 'http://127.0.0.1:8000'
HOST_API = 'http://127.0.0.1:8000/api/v1'
HOST_DOCKER_WKHTMLTOPDF = 'http://localhost:5000/pdf'  # host docker's wkhtmltopdf
PATH_TO_PDF = 'media/temp_pdf'  # path to pdf files


async def worker():
    with redis.Redis() as client:
        while True:
            check_id = client.brpop('checks_id')[1].decode('utf-8')
            url_check = f'{HOST_API}/check/{check_id}/'
            check = requests.get(url_check).content.decode('utf-8')
            check = json.loads(check)

            check_id = check['id']
            ch_type = check['check_type']
            order_id = check['order']['id']

            task = asyncio.create_task(convert_html_to_pdf(f'{HOST}/{ch_type}_check/check_id={check_id}',
                                                           order_id, ch_type, check_id))
            await task


async def convert_html_to_pdf(url_check, order_id, check_type, check_id):
    data = requests.get(url_check).text
    data = base64.b64encode(bytes(data, 'utf-8')).decode('utf-8')
    data = {
        'contents': data,
    }
    headers = {
        'Content-Type': 'application/json',  # This is important
    }
    response = requests.post(HOST_DOCKER_WKHTMLTOPDF, data=json.dumps(data), headers=headers)

    # Save the response contents to a file in the working directory of the worker
    filename = f'{order_id}_{check_type}.pdf'
    upload_pdf_path = f'{PATH_TO_PDF}/{filename}'
    with open(upload_pdf_path, 'wb') as file:
        file.write(response.content)

    # Request to change the status of the check in the DB and send the pdf-file of the check to the server
    check_status = 'rendered'
    await check_status_and_pdf_change(check_id, check_status, upload_pdf_path, filename)


@sync_to_async
def check_status_and_pdf_change(check_id, check_status, upload_pdf_path, filename):
    url = f'{HOST_API}/check/{check_id}/'
    data = {'status': check_status}
    files = {'pdf_file': (filename, open(upload_pdf_path, 'rb'))}
    response = requests.put(url, data=data, files=files)
    print(response.status_code)

    # Deleting a temporary file from an employee's work directory
    if response.status_code == 200 and os.path.exists(f'{PATH_TO_PDF}/{filename}'):
        os.remove(f'{PATH_TO_PDF}/{filename}')


asyncio.run(worker())
