import json
from time import sleep

import requests

HOST = 'http://127.0.0.1:8000'
HOST_API = 'http://127.0.0.1:8000/api/v1'
PATH_TO_PDF = 'media/pdf'

DELAY = 60  # Server polling interval for generated PDF-receipts
KEY = 'key4'  # API printer key


def application():
    if verification(KEY):
        qwery_api = f'{HOST_API}/new_checks/api_key={KEY}'
        while True:
            # Checking the presence of generated PDF-receipts on the server
            checks = requests.get(qwery_api).content.decode('utf-8')
            checks = json.loads(checks)

            if checks:
                # Unpacking the list with existing checks
                for check in checks:
                    check_pdf_name = check['pdf_file'][1:]
                    check_pdf_path = f'{HOST}/{check_pdf_name}'

                    # Download the PDF-check and start printing it
                    check_pdf_file = requests.get(check_pdf_path)
                    with open(check_pdf_name, 'wb') as file:
                        file.write(check_pdf_file.content)

                    # Changing the check status in the DB to "printed"
                    check_status = 'printed'
                    check_id = check['id']
                    check_status_change(check_id, check_status)

            sleep(DELAY)


def check_status_change(check_id, check_status):
    url = f'{HOST_API}/check/{check_id}/'
    data = {'status': check_status}
    response = requests.put(url, data=data)
    print(response.status_code)


def verification(api_key):
    qwery_api = f'{HOST_API}/printer/api_key={api_key}'
    response = requests.get(qwery_api)
    if response.status_code == 200:
        return True
    return False


application()

