from django.conf.urls import include, url
from .views import hello_world
from .views import Doctor

urlpatterns = [
	url(r'^fb/?$',Doctor.as_view()),
	url(r'^doctor/?$',hello_world),
]
