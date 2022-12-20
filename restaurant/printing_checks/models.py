from django.db import models

TYPE_CHOICES = (
    ('client', 'client'),
    ('kitchen', 'kitchen'),
)
STATUS_CHOICES = (
    ('new', 'new'),
    ('rendered', 'rendered'),
    ('printed', 'printed'),
)


class Printer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=False, blank=False, verbose_name='Назва принтера')
    api_key = models.CharField(max_length=128, null=False, blank=False, unique=True, verbose_name='Ключ доступу до API')
    check_type = models.CharField(max_length=128, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0], verbose_name='Тип чеку')
    point_id = models.IntegerField(verbose_name='Номер точки')

    def __str__(self):
        return self.name

class Check(models.Model):
    id = models.AutoField(primary_key=True)
    printer_id = models.ForeignKey(Printer, on_delete=models.CASCADE, default=None, verbose_name='ID принтера')
    type = models.CharField(max_length=128, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0], verbose_name='Тип чеку')
    order = models.JSONField(blank=True, verbose_name='Інформація про замовлення')
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0], verbose_name='Статус чеку')
    pdf_file = models.FileField(blank=True, verbose_name='Посилання на PDF')

    # def __str__(self):
    #     return self.id