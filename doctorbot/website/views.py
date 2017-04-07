from django.http import HttpResponse
from django.shortcuts import render_to_response
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
@api_view(['GET'])
def index_view(requests):
    return render_to_response('index.html')
