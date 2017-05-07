from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import requests
import random
import re
from pprint import pprint
from .models import fb_db


#@ensure_csrf_cookie
verify_token = '00000000'
TOKEN = 'EAAG1BsKUxZB8BALNakB02SE5R3tAf7NyEXF8plOF1SUKkvWWiHwvmi2OoQBqcOqCjJxfRkC9wR7t3kIYv3AfQaZBOTJwfpQQtL7eIMA4z9fhLmApLEDF25iZA99U3RZBZA9WQRnHK7mWjGvmcER2sTZBFo0Ln9AqT8hluFZA5hPGQZDZD'

# Create your views here.
json_dir = '../brain/brain_libs/DST/'
class Doctor(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    post_facebook_message(message['sender']['id'])
                    savetodb(message,message['message']['text'])
        return HttpResponse()

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == verify_token:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error,invalid token')

# def fb_database_init(requests):
    # fb_db.objects.all().delete()
    #savetodb(request, *args, **kwargs)
def savetodb(message,text):
   #message = json.loads(self.request.body.decode('utf-8'))
    #for entry in message['entry']:    
    #    for message in entry['messaging']:
    #        if 'message' != None:
    message = json.dumps(message)
    fb_db.objects.create(content = message,title=text)



# This function should be outside the BotsView class
def post_facebook_message(fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % TOKEN
    with open(json_dir + "DM.json") as json_file:
        line = json.load(json_file)
        line = json.dumps(line)
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": line}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

