#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from .config import ACCTOKEN,VERTOKEN
from .quick_replies import replies
import requests

app = Flask(__name__)
FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
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

    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def handle_postback(recipient_id,text):
    payload = text['payload']
    if payload == "red":
        send_message(recipient_id, "You chose red", "")
    elif payload == "green":
        send_message(recipient_id, "You chose green", "")


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
