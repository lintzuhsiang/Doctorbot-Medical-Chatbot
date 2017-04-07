from django.conf.urls import include, url
from .views import hello_world
from .views import Doctor

urlpatterns = [
	url(r'^bbf803c2a28d7bf5aa984866a317ca4f16f0dd4cda939b3fda/?$',Doctor.as_view())
]
