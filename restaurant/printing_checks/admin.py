from django.contrib import admin
from .models import Printer, Check

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'api_key', 'check_type', 'point_id')
    list_filter = ('name', 'check_type')
@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'printer_id', 'type', 'order', 'status', 'pdf_file')
    list_filter = ('printer_id__name', 'type', 'status')
