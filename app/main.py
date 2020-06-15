#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
from config import ACCTOKEN,VERTOKEN
import requests

app = Flask(__name__)
FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
ACCESS_TOKEN = ACCTOKEN
VERIFY_TOKEN = VERTOKEN
bot = Bot(ACCESS_TOKEN)

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
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_user_msg = ["COVID19","Narendra Modi","Nasarg","Donald Trunp"]
    # sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    response = find_related_urls(random.choice(sample_user_msg))
    return random.choice(response)

def find_related_urls(title):
    """
    args: title of article
    returns: links of  most related articles from trusted sources
    """
    try: 
        from googlesearch import search 
    except ImportError:  
        print("No module named 'google' found")  
    print(title)
    st = " "
    related_urls = []
    # to search 
    query1 = "youtube: "+ title
    query2 = "timesofindia: "+title
    query3 = "hindustantimes: " + title
    for q in search(query1, tld="com", num=10, stop=1, pause=2): 
        st += q
        st += "\n"
        
    for r in search(query2, tld="co.in", num=10, stop=1, pause=2): 
        st += r
        st += "\n"
    for s in search(query3, tld="com", num=10, stop=1, pause=2): 
        st += s
        st += "\n"
    return st

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

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )
    return "success"
