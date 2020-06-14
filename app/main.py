#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from .config import ACCTOKEN,VERTOKEN
from .quick_replies import replies
import requests

app = Flask(__name__)
FB_API_URL = 'https://graph.facebook.com/v7.0/me/messages'
ACCESS_TOKEN = ACCTOKEN
VERIFY_TOKEN = VERTOKEN
notif_token = 0

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
       print (output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text, message['message'])
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
            elif message.get('postback'):
                recipient_id = message['sender']['id']
                handle_postback(recipient_id,message['postback'])
            elif message.get('optin'):
                recipient_id = message['sender']['id']
                handle_optin(recipient_id, message['optin'])

    return "Message Processed"

def handle_optin(recipient_id, optin):
    payload = optin['payload']
    notif_token = optin['one_time_notif_token']
    temp_dict = {}
    temp_dict['text'] = ""
    if payload == "notif":
        send_message(recipient_id, "One time notif token: "+str(optin['one_time_notif_token']), temp_dict)

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def handle_postback(recipient_id,text):
    payload = text['payload']
    temp_dict = {}
    temp_dict['text'] = ""
    if payload == "red":
        send_message(recipient_id, "You chose red", temp_dict)
    elif payload == "green":
        send_message(recipient_id, "You chose green", temp_dict)


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are a dirty fellow!", "Of course I talk like an idiot. How else would u understand me?", "I made a pencil with two erasers. It was pointless.", "What's brown and sticky? A stick."]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, text, message_rec):
    #sends user the text message provided via input response parameter
    """Send a response to Facebook"""
    if(message_rec['text'] == "color"):
        payload = {
        "recipient":{
            "id": recipient_id
        },
        "messaging_type": "RESPONSE",
        "message":{
            "text": "Pick a color:",
            "quick_replies": replies["color"]
        }
        }
    elif (message_rec['text'] == "notif"):
        payload = {
            "recipient": {
                "id":recipient_id
        },
        "message": {
                "attachment": {
                "type":"template",
                "payload": {
                    "template_type":"one_time_notif_req",
                    "title":"Do u want a one-time-notif?",
                    "payload":"notif"
                }
                }
            }
        }
    elif message_rec['text'] == "send notif":
        payload = {
            "recipient": {
                "one_time_notif_token": notif_token
            },
            "message": {
                "text":"One time notif sent"
            }
        }
    elif message_rec.get('quick_reply'):
        if message_rec['quick_reply']['payload'] == 'red':
            payload = {
                'message': {
                    'text': "You chose red"
                },
                'recipient': {
                    'id': recipient_id
                },
                'notification_type': 'regular'
            }
        elif message_rec['quick_reply']['payload'] == 'green':
            payload = {
                'message': {
                    'text': "You chose green"
                },
                'recipient': {
                    'id': recipient_id
                },
                'notification_type': 'regular'
            }
    else:
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
