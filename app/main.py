#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from .config import ACCTOKEN,VERTOKEN
import requests
import logging

app = Flask(__name__)
FB_API_URL = 'https://graph.facebook.com/v7.0/me/messages'
ACCESS_TOKEN = ACCTOKEN
VERIFY_TOKEN = VERTOKEN

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
            elif message.get('postback'):
            	recipient_id = message['sender']['id']
            	handle_postback(recipient_id,message['postback'])

    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def handle_postback(recipient_id,text):
	data = {
	  "recipient":{
	    "id": recipient_id
	  },
	  "messaging_type": "RESPONSE",
	  "message":{
	    "text": "Pick a color:",
	    "quick_replies":[
	      {
	        "content_type":"text",
	        "title":"Red",
	        "payload":"red",
	        "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
	      },{
	        "content_type":"text",
	        "title":"Green",
	        "payload":"green",
	        "image_url":"https://lh3.googleusercontent.com/proxy/4thAzIZQcMhIFwcHQbN6j6OwzoyC-UyHmtxXCn-t5fOMgzZd7oAy4SAfSFMSZDcw1aBjSotVXnw2HDg3v6JKFqahdqu77yFtcqKPJ8iIFWAYLw"
	      }
	    ]
	  }
	}
	response = requests.post(FB_API_URL, headers=headers, params=params, data=data)
	return "success"


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, text):
    #sends user the text message provided via input response parameter
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': ACCESS_TOKEN
    }
    # payload = {
    #     "recipient":{
    #         "id":"recipient_id"
    #     },
    #     "messaging_type": "RESPONSE",
    #     "message":{
    #         "text": "Pick a color:",
    #         "quick_replies":[
    #         {
    #             "content_type":"text",
    #             "title":"Red",
    #         },{
    #             "content_type":"text",
    #             "title":"Green",
    #         }
    #         ]
    #     }
    #     }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )
    return "success"
