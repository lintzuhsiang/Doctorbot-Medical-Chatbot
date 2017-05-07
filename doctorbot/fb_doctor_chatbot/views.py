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

TOKEN = 'EAAG1BsKUxZB8BAKB6qwvZCXbsHSGNKHWMCVuMSS92MI7owsqYMEwAREXksTEq2x3nDO5kJGefmIfJLS7RZBFWegXlhMBR6ChiTNva3wD6ASxNTVomQ0h79ZBAUQgsamtLovGGWbW4MsyFZCY82vP3zcngJgOU8oedNCJvNYcptwZDZD'

# Create your views here.


class Doctor(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("======")
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        
        savetodb(incoming_message)
        return HttpResponse()

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == verify_token:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error,invalid token')

# def fb_database_init(requests):
    # fb_db.objects.all().delete()
    #savetodb(request, *args, **kwargs)
    print("==")
def savetodb(message):
    print("====================")
   #message = json.loads(self.request.body.decode('utf-8'))
    message = json.dumps(message)
    fb_db.objects.create(content = message,title="fb user input")
    print("====================")



# This function should be outside the BotsView class
def post_facebook_message(fbid, recevied_message):

 # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', recevied_message).lower().split()
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % TOKEN
    response_msg = json.dumps(
        {"recipient": {"id": fbid}, "message": {"text": recevied_message}})
    status = requests.post(post_message_url, headers={
                           "Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


def hello_world(request):
    return HttpResponse("Hello world!")
