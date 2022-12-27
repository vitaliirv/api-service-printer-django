import json

import redis

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .models import Printer, Check
from .serializer import PrinterSerializer, CheckSerializer
# from .services import *


def index(request):
    return render(request, 'printing_checks/index.html')


def client_check(request, check_id):
    data = get_check(check_id)
    return render(request, 'printing_checks/client_check.html', data)


def kitchen_check(request, check_id):
    data = get_check(check_id)
    return render(request, 'printing_checks/kitchen_check.html', data)


def get_check(check_id):
    orders = Check.objects.filter(id=check_id)
    data = {}
    if orders:
        data = {'order_id': orders[0].order['id'],
                'price': orders[0].order['price'],
                'address': orders[0].order['address'],
                'client_name': orders[0].order['client']['name'],
                'phone': orders[0].order['client']['phone'],
                'items': orders[0].order['items']
                }
    return data


class PrinterViewSet(viewsets.ModelViewSet):
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer


class CheckViewSet(viewsets.ModelViewSet):
    queryset = Check.objects.all()
    serializer_class = CheckSerializer

    def create(self, request, *args, **kwargs):
        point_id = request.data['point_id']
        order_id = request.data['id']
        serialize_data = []
        param_for_tasks = []

        # Перевіряємо чи є принтери на точці
        printers = Printer.objects.filter(point_id=point_id)
        if not printers:
            return Response({'Помилка, відсутні принтери на точці!'}, status=status.HTTP_404_NOT_FOUND)

        # Створюємо чеки для всіх принтерів точки
        for printer in printers:
            printer_id = printer.id
            ch_type = printer.check_type

            # Перевіряємо наявність згенерованих чеків на дане замовлення
            if self.check_order(order_id, printer_id):
                serializer = self.get_serializer(
                    data={'printer_id': printer_id, 'check_type': ch_type, 'order': request.data})
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                serialize_data.append(serializer.data)

                # Зберігаємо параметри для асинхронних завдань конвертації html чеків в pdf
                check_obj = Check.objects.latest('id')
                # parameters = "{"+f"'check_obj': {check_obj}, 'ch_type': {ch_type}, 'check_id': {check_obj.id}, " \
                #              f"'order_id': {order_id}"+"}"
                # param_for_tasks.append(parameters)
                with redis.Redis() as client:
                    # client.lpush('param_for_tasks', order_id)
                    # client.set('check', check_obj)
                    client.lpush('checks_id', check_obj.id)
                    # client.hset(order_id, 'check_obj', check_obj)
                    # print(client.hget('param_for_task', 'check_obj'))
                    # client.hset(order_id, 'ch_type', ch_type)
        # Стартуємо асинхронний воркер-генератор PDF-файлів
        # Заносимо параметри для асинхронного воркер-генератора PDF-файлів в чергу Redis
        # with redis.Redis() as client:
        #     client.lpush('param_for_tasks', param_for_tasks)
        # asyncio.run(run_tasks(param_for_tasks))

        if not serialize_data:
            return Response({'Помилка, чеки для цього замовлення вже були створені!'}, status=status.HTTP_409_CONFLICT)

        headers = self.get_success_headers(serializer.data)
        return Response(serialize_data, status=status.HTTP_201_CREATED, headers=headers)


    def check_order(self, order_id, printer_id):
        checks = Check.objects.filter(printer_id=printer_id)
        for check in checks:
            if check.order['id'] == order_id:
                return False
        return True

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class CheckDetail(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.check_printer = None

    def get(self, request, *args, **kwargs):
        check_id = kwargs.get("check_id", None)
        api_key = kwargs.get("api_key", None)
        if not check_id and api_key:
            check_status = 'rendered'
            self.checks = Check.objects.filter(status=check_status).filter(printer_id__api_key=api_key)
            return Response(CheckSerializer(self.checks, many=True).data, status=status.HTTP_200_OK)
        self.check_printer = Check.objects.filter(pk=check_id).filter(printer_id__api_key=api_key)
        return Response(CheckSerializer(self.check_printer, many=True).data, status=status.HTTP_200_OK)

    # def put(self, request, *args, **kwargs):
    #     print('111', request.data)
    #     print('333',args, kwargs)
    #     check_id = kwargs['check_id']
    #     request.data['pdf_file'] = request.FILES
    #     # check_status = request.data['status']
    #     self.check = Check.objects.filter(pk=check_id)[0]
    #     if self.check:
    #         serializer = CheckSerializer(data=request.data, instance=self.check, files=request.FILES)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response({"post": serializer.data})
    #     else:
    #         return Response("Method PUT is not allowed")
