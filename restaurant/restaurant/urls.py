"""restaurant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from printing_checks.views import PrinterViewSet, CheckViewSet, CheckDetail

router = routers.SimpleRouter()
router.register(r'printer', PrinterViewSet)
router.register(r'check', CheckViewSet)
router.register(r'create_checks', CheckViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('printing_checks.urls')),
    path('api/v1/new_checks/api_key=<str:api_key>', CheckDetail.as_view()),
    # path('api/v1/update_check/check_id=<int:check_id>', CheckDetail.as_view()),
    path('api/v1/check/check_id=<int:check_id>&api_key=<str:api_key>', CheckDetail.as_view()),
    path('api/v1/', include(router.urls)),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)