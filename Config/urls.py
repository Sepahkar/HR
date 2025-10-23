"""Config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import json

from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from HR.backends import check_auth_user,show_403,show_404
from django.shortcuts import reverse
from django.http.response import HttpResponse,HttpResponseRedirect
import requests
from HR.utils import get_all_apps
from django.shortcuts import render
from HR.decorators import public_view



def tt(request):
    #return render(request,"HR/tt.html")
    return HttpResponse(f"yearnumber is ")


def api_tt(request):
    return HttpResponse(str(request.META.get('HTTP_AUTHORIZATION')))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('CheckAuthUser/', check_auth_user, name="check_auth_user"),
    path('error/', include("HR.urls_error")),
    path('Duties/', include('Duties.urls')),
    path('HR/api/user/', include('HR.user_urls')),
    path('HR/', include('HR.urls')),
    path('tt/', tt),
    path('api/tt/', api_tt),

]



urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL_EIT,document_root=settings.STATIC_ROOT_EIT)
urlpatterns+=static(settings.MEDIA_URL_HR,document_root=settings.MEDIA_ROOT_HR)
