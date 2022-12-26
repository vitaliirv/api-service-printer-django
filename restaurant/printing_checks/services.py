import json

import asyncio
import requests
import base64

from asgiref.sync import sync_to_async

HOST = 'http://127.0.0.1:8000'
HOST_DOCKER_WKHTMLTOPDF = 'http://localhost:5000/pdf'  # host docker's wkhtmltopdf


async def run_tasks(param_for_tasks):
    tasks = []
    for param in param_for_tasks:
        check_obj = param['check_obj']
        ch_type = param['ch_type']
        check_id = param['check_id']
        order_id = param['order_id']
        tasks.append(asyncio.create_task(convert_html_to_pdf(f'{HOST}/{ch_type}_check/check_id='
                                                             f'{check_id}', order_id, ch_type, check_obj)))
    for task in tasks:
        await task


async def convert_html_to_pdf(url_check, order_id, check_type, check_obj):
    data = requests.get(url_check).text
    data = base64.b64encode(bytes(data, 'utf-8')).decode('utf-8')
    data = {
        'contents': data,
    }
    headers = {
        'Content-Type': 'application/json',  # This is important
    }
    response = requests.post(HOST_DOCKER_WKHTMLTOPDF, data=json.dumps(data), headers=headers)

    # Save the response contents to a file
    upload_pdf_path = f'media/pdf/{order_id}_{check_type}.pdf'
    with open(upload_pdf_path, 'wb') as f:
        f.write(response.content)

    # Змінюємо статус чека та вносимо посилання на pdf-файл чека в БД
    check_status = 'rendered'
    await check_status_and_pdfurl_change(check_obj, check_status, upload_pdf_path[6:])


@sync_to_async
def check_status_and_pdfurl_change(check, status, pdf_file):
    return check.update(status, pdf_file)
