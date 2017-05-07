from django.conf.urls import include, url
from .views import Doctor
from .admin import admin

urlpatterns = [
	url(r'^fb/?$',Doctor.as_view()),
	url(r'^admin/',include(admin.site.urls)),
]
