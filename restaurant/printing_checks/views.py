import redis

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .models import Printer, Check
from .serializer import PrinterSerializer, CheckSerializer


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


def verification(api_key):
    printer = Printer.objects.filter(api_key=api_key)
    if printer:
        return printer[0]
    return False


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

        # Checking the availability of printers at the point
        printers = Printer.objects.filter(point_id=point_id)
        if not printers:
            return Response({'error': 'No printer is configured for this point!'}, status=status.HTTP_404_NOT_FOUND)

        # Creating receipts for all printers at the point
        for printer in printers:
            printer_id = printer.id
            ch_type = printer.check_type

            # Checking the availability of already generated checks for this order
            if self.check_order(order_id, printer_id):
                serializer = self.get_serializer(
                    data={'printer_id': printer_id, 'check_type': ch_type, 'order': request.data})
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                serialize_data.append(serializer.data)

                # Formation of parameters for an asynchronous working generator
                # of PDF files and queued for execution through the Redis service
                check_obj = Check.objects.latest('id')
                with redis.Redis() as client:
                    client.lpush('checks_id', check_obj.id)

        if not serialize_data:
            return Response({'error': 'Checks have already been created for this order!'},
                            status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({'ok': 'Checks have been created successfully!'},
                        status=status.HTTP_200_OK, headers=headers)

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

        if api_key and verification(api_key):
            if not check_id and api_key:
                check_status = 'rendered'
                self.checks = Check.objects.filter(status=check_status).filter(printer_id__api_key=api_key)
                return Response({"checks": CheckSerializer(self.checks, many=True).data}, status=status.HTTP_200_OK)

            self.check_printer = Check.objects.filter(pk=check_id).filter(printer_id__api_key=api_key)
            if self.check_printer:
                return Response(CheckSerializer(self.check_printer, many=True).data, status=status.HTTP_200_OK)
            return Response({'error':'This check does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Authorization error!'}, status=status.HTTP_401_UNAUTHORIZED)


class PrinterDetail(APIView):
    def get(self, request, *args, **kwargs):
        api_key = kwargs.get("api_key", None)
        if api_key and verification(api_key):
            return Response({'ok': 'ok'}, status=status.HTTP_200_OK)

        return Response({'error': 'Authorization error!'}, status=status.HTTP_401_UNAUTHORIZED)
