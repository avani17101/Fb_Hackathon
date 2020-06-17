# Python libraries that we need to import for our bot
import random
import os
from flask import Flask, request
from flask_pymongo import pymongo
from .config import ACCTOKEN, VERTOKEN, DB_URL
import requests
import datetime
from .quick_replies import replies, generate_app_slots, generate_reminder_slots
from apscheduler.schedulers.background import BackgroundScheduler

MONGO_URL = DB_URL

app = Flask(__name__)
client = pymongo.MongoClient(MONGO_URL)
db = client.friend_indeed

FB_API_URL = "https://graph.facebook.com/v7.0/me/messages"
ACCESS_TOKEN = ACCTOKEN
VERIFY_TOKEN = VERTOKEN
pool = []
notif_token = 0
cur_slots = []
available_slots = []
anonymous_usernames =  ['pigeon', 'seagull', 'bat', 'owl', 'sparrows', 'robin', 'bluebird', 'cardinal', 'hawk', 'fish', 'shrimp', 'frog', 'whale', 'shark', 'eel', 'seal', 'lobster', 'octopus', 'mole', 'shrew', 'rabbit', 'chipmunk', 'armadillo', 'dog', 'cat', 'lynx', 'mouse', 'lion', 'moose', 'horse', 'deer', 'raccoon', 'zebra', 'goat', 'cow', 'pig', 'tiger', 'wolf', 'pony', 'antelope', 'buffalo', 'camel', 'donkey', 'elk', 'fox', 'monkey', 'gazelle', 'impala', 'jaguar', 'leopard', 'lemur', 'yak', 'elephant', 'giraffe', 'hippopotamus', 'rhinoceros', 'grizzlybear']
def send_request(payload):
    auth = {"access_token": ACCESS_TOKEN}
    response = requests.post(FB_API_URL, params=auth, json=payload)
    return "success"

# We will receive messages that Facebook sends our bot at this endpoint
def check_one_time_notif():
    time_now = datetime.datetime.now().strftime("%H:%M")
    for i in db.one_time_notif.find({ "notif_time" : time_now}):
        payload = {
            "recipient": {"one_time_notif_token": i["notif_token"]},
            "message": {"text": "You have an appointment at "+i["app_time"]},
        }
        send_request(payload)

sched = BackgroundScheduler()
sched.add_job(check_one_time_notif, 'cron',minute='0,10,20,30,40,50')
sched.start()
@app.route("/", methods=["GET", "POST"])
def receive_message():
    if request.method == "GET":
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        print(output)
        for event in output["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                if message.get("message"):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message["sender"]["id"]
                    if message["message"].get("text"):
                        response_sent_text = get_message()
                        send_message(
                            recipient_id, response_sent_text, message["message"]
                        )
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message["message"].get("attachments"):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
                elif message.get("postback"):
                    recipient_id = message["sender"]["id"]
                    handle_postback(recipient_id, message["postback"])
                elif message.get("optin"):
                    recipient_id = message["sender"]["id"]
                    handle_optin(recipient_id, message["optin"])

    return "Message Processed"


def handle_optin(recipient_id, optin):
    payload = optin["payload"]
    notif_token = optin["one_time_notif_token"]
    temp_dict = {}
    temp_dict["text"] = ""
    if payload == "notif":
        send_message(
            recipient_id,
            "One time notif token: " + str(optin["one_time_notif_token"]),
            temp_dict,
        )
    elif payload.startswith("reminder"):
        payload_list = payload.split(" ")
        one_time_notif_dict = {
            "app_time" : payload_list[2],
            "notif_time" : payload_list[1],
            "notif_token" : optin["one_time_notif_token"]
        }
        db.one_time_notif.insert_one(one_time_notif_dict)
        send_message(
            recipient_id, "You will be notified at " + payload_list[1], temp_dict,
        )


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"


def handle_postback(recipient_id, text):
    payload = text["payload"]
    temp_dict = {}
    temp_dict["text"] = ""
    if payload == "red":
        send_message(recipient_id, "You chose red", temp_dict)
    elif payload == "green":
        send_message(recipient_id, "You chose green", temp_dict)


# chooses a random message to send to the user
def get_message():
    sample_responses = [
        "You are a dirty fellow!",
        "Of course I talk like an idiot. How else would u understand me?",
        "I made a pencil with two erasers. It was pointless.",
        "What's brown and sticky? A stick.",
    ]
    # return selected item to the user
    return random.choice(sample_responses)


def send_message(recipient_id, text, message_rec):
    # sends user the text message provided via input response parameter
    """Send a response to Facebook"""
    if message_rec["text"] == "Talk to someone":
        user_name = "Anonymous "+anonymous_usernames[random.randint(0,len(anonymous_usernames)-1)]
        print (user_name)
        if (len(pool)==0):
            print ("Adding to pool")
            pool.append({"id":recipient_id,"timestamp": datetime.datetime.now().strftime("%H:%M"),"username":user_name})
            payload = {
                "message": {"text": "Please wait for 1 min for us to pair you with someone else"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        else:
            print ("Someone is there in pool")
            partner_id = pool[0]["id"]
            partner_username = pool[0]["username"]
            if (partner_id!=recipient_id):
                pool[:] = []
                payload_partner = {
                "message": {"text": "Congrats! You have been paired with "+str(user_name)},
                "recipient": {"id": partner_id},
                "notification_type": "regular",
                }
                payload = {
                "message": {"text": "Congrats! You have been paired with "+str(partner_username)},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
                }
                send_request(payload_partner)
            else:
                payload = {
                "message": {"text": "Please wait for 1 min for us to pair you with someone else"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
    elif message_rec["text"] == "Book an appointment":
        cur_slots = []
        available_slots = []
        psych = db.psych.find_one({"name": "Dr. Dipanwita"})
        cur_slots = psych["time"]
        available_slots = psych["is_available"]
        payload = {
            "message": {
                "text": "Pick a time slot when you'll be available:",
                "quick_replies": generate_app_slots(cur_slots, available_slots),
            },
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "notification_type": "regular",
        }
        print(payload)
    elif message_rec["text"] == "color":
        payload = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": "Pick a color:", "quick_replies": replies["color"]},
        }
    elif message_rec.get("quick_reply"):
        if message_rec["quick_reply"]["payload"] == "red":
            payload = {
                "message": {"text": "You chose red"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        elif message_rec["quick_reply"]["payload"] == "green":
            payload = {
                "message": {"text": "You chose green"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        elif message_rec["quick_reply"]["payload"].startswith("appointment"):
            app_time = datetime.datetime.strptime(
                message_rec["quick_reply"]["payload"].split(" ")[1], "%H:%M"
            )

            payload = {
                "recipient": {"id": recipient_id},
                "messaging_type": "RESPONSE",
                "message": {
                    "text": "Pick a reminder time:",
                    "quick_replies": generate_reminder_slots(app_time),
                },
            }
        elif message_rec["quick_reply"]["payload"].startswith("reminder"):
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "one_time_notif_req",
                            "title": 'Select "notify me" to confirm the reminder?',
                            "payload": message_rec["quick_reply"]["payload"],
                        },
                    }
                },
            }
    else:
        payload = {
            "message": {"text": text},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    send_request(payload)
