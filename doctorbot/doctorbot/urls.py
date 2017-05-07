"""django_react_boilerplate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from fb_doctor_chatbot.views import Doctor
from fb_doctor_chatbot.views import hello_world


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('website.urls')),
    url(r'^', include('hospital_crawler.urls')),
    url(r'^docs/', include('rest_framework_docs.urls')),
    url(r'^fb_doctor_chatbot/',include('fb_doctor_chatbot.urls')),

]
