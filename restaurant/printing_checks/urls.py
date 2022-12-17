from django.urls import path
from printing_checks.views import *

urlpatterns = [
    path('', index, name='home')
]
