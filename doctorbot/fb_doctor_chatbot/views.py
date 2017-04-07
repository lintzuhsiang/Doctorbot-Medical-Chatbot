from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse


TOKEN = 'AG1BsKUxZB8BAIwX45aWjehyGbfqWgu7DVVorr4qhe77V9mrtETGurNiUH45z7nPAhM2A68yNDZCSvb9dZB8UyTB9p3DUz6hpnVjiQlgKVNrDmJa6n3PXDxc9NKYhIZC4f7LdZA7qjYFdEXsD3FtzCxaQKlC83VFIvUqko7V6gZDZD'

# Create your views here.
class Doctor(generic.View):
	#@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return generic.View.dispatch(self,request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		incoming_message = json.loads(self.request.body.decode('utf-8'))
		for entry in incoming_message['entry']:
			for message in entry['messaging']:
				if 'message' in message:
					pprint(message)
					post_facebook_message(message['sender']['id'], message['message']['text'])
		return HttpResponse()

	def get(self,request,*args,**kwargs):
		if self.request.GET== TOKEN :
			return HttpResponse(self.request.GET['hub.challenge'])
		else:
			return HttpResponse('Error,invalid token')




jokes = {
         'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
                    """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""],
         'fat':    ["""Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""",
                    """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """],
         'dumb':   ["""Yo' Mama is so dumb, when God was giving out brains, she thought they were milkshakes and asked for extra thick.""",
                    """Yo' Mama is so dumb, she locked her keys inside her motorcycle."""] 
         }
# This function should be outside the BotsView class
def post_facebook_message(fbid, recevied_message):           

 # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    joke_text = ''
    for token in tokens:
        if token in jokes:
            joke_text = random.choice(jokes[token])
            break
    if not joke_text:
        joke_text = "I didn't understand! Send 'stupid', 'fat', 'dumb' for a Yo Mama joke!"

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=<page-access-token>' 
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

def hello_world(request):
	return HttpResponse("Hello world!!!!!!!!")
