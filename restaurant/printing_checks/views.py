from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .models import Printer, Check
from .serializer import PrinterSerializer, CheckSerializer


def index(request):
    return render(request, 'printing_checks/client_check.html')


class PrinterViewSet(viewsets.ModelViewSet):
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer


class CheckViewSet(viewsets.ModelViewSet):
    queryset = Check.objects.all()
    serializer_class = CheckSerializer

    def create(self, request, *args, **kwargs):
        point_id = request.data['point_id']
        order_id = request.data['id']
        printers = Printer.objects.filter(point_id=point_id)
        serialize_data = []
        if not printers:
            return Response({'Помилка, відсутні принтери на точці!'}, status=status.HTTP_404_NOT_FOUND)

        for printer in printers:
            printer_id = printer.id
            ch_type = printer.check_type
            if self.check_order(order_id, printer_id):
                serializer = self.get_serializer(data={'printer_id': printer_id, 'type': ch_type, 'order': request.data})
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                serialize_data.append(serializer.data)

        if not serialize_data:
            return Response({'Помилка, чеки для цього замовлення вже були створені!'}, status=status.HTTP_409_CONFLICT)

        headers = self.get_success_headers(serializer.data)
        return Response(serialize_data, status=status.HTTP_201_CREATED, headers=headers)

    def check_order(self, order_id, printer_id):
        if Check.objects.filter(printer_id=printer_id)[0].order['id'] == order_id:
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
        self.check_printer = Check.objects.filter(pk=check_id).filter(api_key=api_key)
        return Response(CheckSerializer(self.check_printer, many=True).data, status=status.HTTP_200_OK)
