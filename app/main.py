# Python libraries that we need to import for our bot
import schedule
import random
import os
from flask import Flask, request
from flask_pymongo import pymongo
from .config import ACCTOKEN, VERTOKEN, DB_URL
from .data import anonymous_usernames
import requests
import datetime
from .quick_replies import replies, generate_app_slots, generate_reminder_slots
from apscheduler.schedulers.background import BackgroundScheduler
from .wit_conv import wit_response
from .conversation import *
MONGO_URL = DB_URL

app = Flask(__name__)
client = pymongo.MongoClient(MONGO_URL)
db = client.friend_indeed

FB_API_URL = "https://graph.facebook.com/v7.0/me/messages"
FB_PERSONA_URL = "https://graph.facebook.com/me/personas"
ACCESS_TOKEN = ACCTOKEN
VERIFY_TOKEN = VERTOKEN
pool = []
notif_token = 0
cur_slots = []
available_slots = []
reported_person = 0
def send_request(payload):
    auth = {"access_token": ACCESS_TOKEN}
    response = requests.post(FB_API_URL, params=auth, json=payload)
    return "success"

def send_persona_request(payload):
    auth = {"access_token": ACCESS_TOKEN}
    response = requests.post(FB_PERSONA_URL, params=auth, json=payload)
    persona_id =  response.json()["id"]
    print ("I'm in function ",persona_id)
    return persona_id

# We will receive messages that Facebook sends our bot at this endpoint
def check_one_time_notif():
    time_now = datetime.datetime.now().strftime("%H:%M")
    for i in db.one_time_notif.find({"notif_time": time_now}):
        payload = {
            "recipient": {"one_time_notif_token": i["notif_token"]},
            "message": {"text": "You have an appointment at " + i["app_time"]},
        }
        send_request(payload)

def one_minute_jobs():
    minute_delta = datetime.timedelta(hours=0, minutes=1, seconds=0)
    removed = []
    for i in db.pool.find({}):
        if datetime.datetime.now() - i["timestamp"] > minute_delta:
            db.pool.remove({"id" : i["id"]})
            print("yayy1")
            payload = {
                "recipient": {"id": i["id"]},
                "message": {"text": "Sorry! We couldn't find anyone at this moment. Try again after some time."},
            }
            send_request(payload)
    
        

def check_id(id):
    check_user = db.user_status.find_one({"user": id})
    if check_user is None:
        db.user_status.insert_one({"user": id, "status": 0})
        return 0
    else:
        return check_user["status"]


sched = BackgroundScheduler()
sched.add_job(check_one_time_notif, "cron", minute="0,10,20,30,40,50")
sched.start()

sched = BackgroundScheduler()
sched.add_job(one_minute_jobs, "cron", minute="0-59")
sched.start()

def remove_conncetion(person,message,recipient_id):
    db.paired_peeps.remove({"fp":person["fp"],"sp":person["sp"]})
    db.user_status.update_one({"user": person["sp"]}, {"$set": {"status": 0}})
    db.user_status.update_one({"user": person["fp"]}, {"$set": {"status": 0}})
    if person["fp"] == message["sender"]["id"]:
        reported_person =  person["sp"]
    else:
        reported_person =  person["fp"]
    print(reported_person)
    payload = {
        "recipient": {"id": message["sender"]["id"]},
        "notification_type": "regular",
        "message": {
            "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":"You reported your partner. Help us identify the issue!",
                "buttons":[
                    {
                        "type":"postback",
                        "title":"Harassment/bullying",
                        "payload" : "harass"
                    },
                    {
                        "type":"postback",
                        "title":"Rude/insensitive",
                        "payload" : "rude"
                    },
                    {
                        "type":"postback",
                        "title":"Prankster/troll",
                        "payload" : "troll"
                    }
                ]
                }
            }
        },
    }
    payload_partner = {
    "recipient": {"id": recipient_id},
    "notification_type": "regular",
    "message": {
        "text": "We are sorry but your partner reported you. The admins will review the report and get back to you."
    },
    }
    return payload
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
        #print(output)
        for event in output["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                recipient_id = message["sender"]["id"]
                status = check_id(message["sender"]["id"])
                if status//10 == 0:
                    if message.get("message"):
                        # Facebook Messenger ID for user so we know where to send response back to
                        if (message["message"].get("attachments")):
                            print("Attachment not supported")
                        if message["message"].get("text"):
                            response_sent_text = get_message()
                            send_message(
                                recipient_id, response_sent_text, message["message"]
                            )
                    elif message.get("postback"):
                        handle_postback(recipient_id, message["postback"])
                    elif message.get("optin"):
                        handle_optin(recipient_id, message["optin"])
                elif status//10 == 1:
                    if status % 10 == 0:
                        cur_speaker = ""
                        persona_id_cur = ""
                        person = db.paired_peeps.find_one({"fp": message["sender"]["id"]})
                        if message.get("message"):
                            if person is None:
                                person = db.paired_peeps.find_one(
                                    {"sp": message["sender"]["id"]}
                                )
                                recipient_id = person["fp"]
                                cur_speaker = "sp"
                                persona_id_cur = person["persona_id_sp"]
                            else:
                                recipient_id = person["sp"]
                                cur_speaker = "fp"
                                persona_id_cur = person["persona_id_fp"]
                            response_sent_text = message["message"]["text"]
                            if (response_sent_text=="/end"):
                                db.paired_peeps.remove({"fp":person["fp"],"sp":person["sp"]})
                                db.user_status.update_one({"user": person["sp"]}, {"$set": {"status": 0}})
                                db.user_status.update_one({"user": person["fp"]}, {"$set": {"status": 0}})
                                payload = {
                                "recipient": {"id": message["sender"]["id"]},
                                "notification_type": "regular",
                                "message": {
                                    "text": "The chat ended. We hope you feel better. Please take some time to rate your partner.", "quick_replies": replies["end_rating"]
                                },
                                }
                                payload_partner = {
                                "recipient": {"id": recipient_id},
                                "notification_type": "regular",
                                "message": {
                                    "text": "The chat ended. We hope you feel better. Please take some time to rate your partner.", "quick_replies": replies["end_rating"]
                                },
                                }
                                send_request(payload_partner)
                            elif (response_sent_text=="/report"):
                                remove_conncetion(person,message,recipient_id)

                                send_request(payload_partner)
                            else:
                                payload = {
                                    "recipient": {"id": recipient_id},
                                    "notification_type": "regular",
                                    "message": {
                                        "text": response_sent_text
                                    },
                                    "persona_id": persona_id_cur
                                }
                            print("mesages sent")
                            send_request(payload)
                            timestamp_str = "timestamp_"+cur_speaker
                            db.paired_peeps.update_one({cur_speaker: person[cur_speaker]}, {"$set": {timestamp_str: datetime.datetime.now()}})
                    elif status % 10 == 1:
                        db.user_status.update_one({"user": message["sender"]["id"]}, {"$set": {"status": 0}})
                        # if message.get("message"): 
                        #     try:
                        #         print(message["message"]["text"], reported_person)
                        #     except:
                        #         print("Error")
                        #     report = {
                        #         sender : message["sender"]["id"],
                        #         reported_person_id : reported_person,
                        #         report_text : message["message"]["text"]
                        #     }
                            
                        #     db.report.insert_one(report)
                        #     temp_dict = {}
                        #     temp_dict["text"] = "" 
                        #     send_message(message["sender"]["id"], "Your report has been noted. We will come back to you soon. Take care!", )
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
            "app_time": payload_list[2],
            "notif_time": payload_list[1],
            "notif_token": optin["one_time_notif_token"],
        }
        db.one_time_notif.insert_one(one_time_notif_dict)
        send_message(
            recipient_id, "You will be notified at " + payload_list[1], temp_dict,
        )

def handle_postback(recipient_id, postback):
    payload = postback["payload"]
    temp_dict = {}
    temp_dict["text"] = ""
    if payload in ['harass', 'rude', 'troll']:
        db.user_status.update_one({"user": recipient_id}, {"$set": {"status": 11}})
        send_message(recipient_id, "Describe ur problem", temp_dict)

def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"


# chooses a random message to send to the user
def get_message():

    return "Hiii am in test mode"

def talk_to_someone(recipient_id, text, message_rec):
     if message_rec["text"] == "Talk to someone":
        user_name = (
            "Anonymous "
            + anonymous_usernames[random.randint(0, len(anonymous_usernames) - 1)]
        )
        pool = db.pool.find({})
        print(user_name)
        if pool.count() == 0:
            print("Adding to pool")
            temp_pool = {
                "id": recipient_id,
                "timestamp": datetime.datetime.now(),
                "username": user_name,
            }
            db.pool.insert_one(temp_pool)
            
            payload = {
                "message": {
                    "text": "Please wait for 1 min for us to pair you with someone else"
                },
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        else:
            print("Someone is there in pool")
            partner_id = pool[0]["id"]
            partner_username = pool[0]["username"]
            if partner_id != recipient_id:
                # pool[:] = []
                db.pool.remove({"id" : partner_id})
                persona_id_self = send_persona_request({
                    "name":user_name,
                    "profile_picture_url":"https://image.shutterstock.com/image-photo/young-girl-making-funny-faces-260nw-343761566.jpg"
                    })
                payload_partner = {
                    "message": {
                        "text": "Congrats! You have been paired with " + str(user_name)
                    },
                    "recipient": {"id": partner_id},
                    "notification_type": "regular",
                    "persona_id": persona_id_self
                }
                persona_id = send_persona_request({
                    "name":partner_username,
                    "profile_picture_url":"https://image.shutterstock.com/image-photo/young-girl-making-funny-faces-260nw-343761566.jpg"
                    })
                payload = {
                    "message": {
                        "text": "Congrats! You have been paired with "
                        + str(partner_username)
                    },
                    "recipient": {"id": recipient_id},
                    "notification_type": "regular",
                    "persona_id": persona_id
                }
                print (persona_id_self,persona_id)
                db.user_status.update_one(
                    {"user": recipient_id}, {"$set": {"status": 10}}
                )

                db.user_status.update_one({"user": partner_id}, {"$set": {"status": 10}})
                db.paired_peeps.insert_one({"fp": recipient_id, "sp": partner_id, "persona_id_sp": persona_id,"persona_id_fp": persona_id_self,"timestamp_fp" : datetime.datetime.now(),"timestamp_sp" : datetime.datetime.now()})
                send_request(payload_partner)
            else:
                payload = {
                    "message": {
                        "text": "Please wait for 1 min for us to pair you with someone else"
                    },
                    "recipient": {"id": recipient_id},
                    "notification_type": "regular",
                }
            return payload

def getYoga_displayed(recipient_id):
    url = suggest_yoga()
    payload = {
            "message": {"text": "here is yoga aasan for you! url:"+str(url)},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    return payload

talk_to_asked=0
yoga_ask=0
def send_message(recipient_id, text, message_rec):
    # sends user the text message provided via input response parameter
    """Send a response to Facebook"""
    entity, value = wit_response(message_rec["text"])
    global talk_to_asked
    global yoga_ask
    if(entity=='yes'and yoga_ask==1 ):
        yoga_ask=0
        payload = getYoga_displayed(recipient_id)



    if(entity=='yes' and talk_to_asked==1):
        talk_to_asked=0
        payload = talk_to_someone(recipient_id, text, message_rec)

    if(entity=='No' and talk_to_asked==1):
        # if possible this image url or random from a set https://www.happiness.com/en/uploads/monthly_2019_08/suicide-prevention-quotes.png.8871cc34504ac992dda77928ebb0e60e.png
        payload = {
                "message": {"text": "Okay, it's natural to feel you don't want to talk to anyone, but you know it always helps. Here is a qoute for you: “Soak up the views. Take in the bad weather and the good weather. You are not the storm.” Matt Haig"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
    
    
    if(entity=='Depressed'):
        payload = {
                "message": {"text": "I am here to listen to you, would you like to talk to your fellow buddy?"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        talk_to_asked = 1


    if(entity== 'suicidal'):
        
        payload = {
            "message": {"text": "You know life is very precious and you are invalauble to me. I am here to listen to you, would you like to talk to your fellow buddy?"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
        talk_to_asked = 1

        #if no: motivating quote, ask for yoga(intent WantYoga)/music(intent MusicListen)
    
    if(entity =='happy'):
        payload = {
            "message": {"text": "That's so good, do remain happy, it's the purpose of life"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    if(entity== 'wantYoga'):
        payload = getYoga_displayed(recipient_id)

    if(entity=='likedYoga'):
        payload = {
            "message": {"text": "It's good you liked it, would you like to do some more Aasan's now?"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        } 
        yoga_ask = 1

    if(entity== 'MusicListen'):
        url = suggest_songs()
        payload = {
            "message": {"text": "here is music for you! url:"+str(url)},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
       
    if(entity=="hatespeech" or entity=="threat" or entity=="privacyViolation"):
        # end connection: not implemented yet
        payload = {
            "message": {"text": "We are sorry this connection voilates our code of conduct by using threat/hatespeech and it will be reported"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    if(entity== 'jokes'):
        url = suggest_songs()
        payload = {
            "message": {"text": "here is joke for you, enjoy!"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        } 
    if(entity== 'memes'):
        url = suggest_songs()
        payload = {
            "message": {"text": "here is a funny meme for you!"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        } 

    if(entity == "psychologist_schduling"):
        #elif message_rec["text"] == "Book an appointment":
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
        elif message_rec["quick_reply"]["payload"] == "good":
            payload = {
                "message": {"text": "We look forward to it!"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        elif message_rec["quick_reply"]["payload"] == "medium":
            payload = {
                "message": {"text": "Thanks"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
        elif message_rec["quick_reply"]["payload"] == "bad":
            payload = {
                "message": {"text": "We promise to be better next time"},
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