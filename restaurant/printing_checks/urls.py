from django.urls import path
from printing_checks.views import *

urlpatterns = [
    path('', index, name='home'),
    path('client_check/check_id=<int:check_id>', client_check, name='client_check'),
    path('kitchen_check/check_id=<int:check_id>', kitchen_check, name='kitchen_check')
]
