"""PCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin

from PCRM import views

urlpatterns = [
    url(r'^$', views.index),#全局的index
    url(r'^admin/', admin.site.urls),
    url(r'^crm/', include('crm.urls')),#以crm开头的网址，都到crm文件夹里的urls.py里面去找
    url(r'^student/', include('student.urls')),
    url(r'^king_admin/', include('king_admin.urls')),
    url(r'^account/login/', views.account_login),#全局的login
    url(r'^account/logout/', views.account_logout,name='acc_logout'),#全局的login

]
