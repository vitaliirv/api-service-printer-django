from django.shortcuts import render

def index(request):
    return render(request, 'printing_checks/base.html')