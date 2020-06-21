# Python libraries that we need to import for our bot
import schedule
import random
import os
from flask import Flask, request
from flask_pymongo import pymongo
from .config import ACCTOKEN, VERTOKEN, DB_URL
from .data import *
from .handle_standby import *
from .fb_requests import *
from .psych import *
import requests
import datetime
from .quick_replies import *
from apscheduler.schedulers.background import BackgroundScheduler
from .book_appointment import *
from .talk_to_someone import *
from .handle_optin import *
from .handle_postback import *
from .handle_quickreply import *
from .handle_normal_message import *
from .random_message import *
from .send_message import *

from .utils import *

MONGO_URL = DB_URL

app = Flask(__name__)
client = pymongo.MongoClient(MONGO_URL)
db = client.friend_indeed
ACCESS_TOKEN = ACCTOKEN
VERIFY_TOKEN = VERTOKEN
pool = []
notif_token = 0
cur_slots = []
available_slots = []
reported_person = 0

# We will receive messages that Facebook sends our bot at this endpoint
def check_one_time_notif():
    time_now = datetime.datetime.now().strftime("%H:%M")
    for i in db.one_time_notif.find({"notif_time": time_now}):
        payload = {
            "recipient": {"one_time_notif_token": i["notif_token"]},
            "message": {"text": "You have an appointment at " + i["app_time"]},
        }
        send_request(payload)
def check_appointment():
    time_now = datetime.datetime.now().strftime("%H:%M")
    date_now = datetime.datetime.now().strftime("%d.%m.%Y")
    #print ("yay")
    print (time_now,date_now)
    for i in db.appointment.find({"time":time_now,"date":date_now,"appointment_status":"1"}):
        therapist = i["therapist_id"]
        user = i["appointed_id"]
        db.user_status.update_one({"user":user},{"$set":{"status":30}})
        db.user_status.update_one({"_id":therapist},{"$set":{"status":91}})
        therapist_id = (db.user_status.find_one({"_id":therapist}))["user"]
        print (therapist_id,user)
        db.paired_peeps.insert_one({"fp": therapist_id, "sp": user, "timestamp_fp" : datetime.datetime.now(),"timestamp_sp" : datetime.datetime.now()})


def one_minute_jobs():
    minute_delta = datetime.timedelta(hours=0, minutes=1, seconds=0)
    removed = []
    sorry_text(db,minute_delta)
    # for i in db.pool.find({}):
    #     if datetime.datetime.now() - i["timestamp"] > minute_delta:
    #         db.pool.remove({"id" : i["id"]})
    #         print("yayy1")
    #         payload = {
    #             "recipient": {"id": i["id"]},
    #             "message": {"text": "Sorry! We couldn't find anyone at this moment. Try again after some time."},
    #         }
    #         send_request(payload)
    


def check_id(id):
    check_user = db.user_status.find_one({"user": id})
    if check_user is None:
        db.user_status.insert_one({"user": id, "status": 0,"joke_calls":0})
        db.joke_categories.insert_one({"user":id,"score0":20})
        db.joke_categories.insert_one({"user":id,"score1":20})
        db.joke_categories.insert_one({"user":id,"score2":20})
        db.joke_categories.insert_one({"user":id,"score3":20})
        return 0
    else:
        return check_user["status"]


sched = BackgroundScheduler()
sched.add_job(check_one_time_notif, "cron", minute="0,10,20,30,40,50")
sched.start()

sched = BackgroundScheduler()
sched.add_job(one_minute_jobs, "cron", minute="0-59")
sched.start()

sched2 = BackgroundScheduler()
sched2.add_job(check_appointment, "cron", minute="0,30")
sched2.start()

@app.route("/main", methods=["GET", "POST"])
def receive_message():
    if request.method == "GET":
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        print("abc")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        print(output)
        for event in output["entry"]:
            if (event.get("messaging")):
                messaging = event["messaging"]
                for message in messaging:
                    recipient_id = message["sender"]["id"]
                    status = check_id(message["sender"]["id"])
                    if status//10 == 0:
                        if message.get("message"):
                            handle_normal_message(db,recipient_id,message)
                        elif message.get("postback"):
                            handle_postback(db, recipient_id, message["postback"])
                        elif message.get("optin"):
                            handle_optin(db, recipient_id, message["optin"])
                    elif status//10==9:
                        if (status%10==1):
                            cur_speaker = ""
                            persona_id_cur = ""
                            person = db.paired_peeps.find_one({"fp": message["sender"]["id"]})
                            if message.get("message"):
                                response_sent_text = message["message"]["text"]
                                if (response_sent_text=="/end"):
                                    db.paired_peeps.remove({"fp":person["fp"],"sp":person["sp"]})
                                    db.user_status.update_one({"user": person["sp"]}, {"$set": {"status": 0}})
                                    db.user_status.update_one({"user": person["fp"]}, {"$set": {"status": 90}})
                                    payload_partner = {
                                        "message": {
                                            "text": "The chat ended. Hope we could help you."
                                        },
                                        "recipient": {"id": person["sp"]},
                                        "notification_type": "regular"
                                    }
                                    send_request(payload_partner)
                                    payload = {
                                        "recipient": {"id": person["fp"]},
                                        "notification_type": "regular",
                                        "message": {
                                            "text": "The chat ended. Thank you for your time!"
                                        },
                                    }
                                else:
                                    payload = {
                                        "recipient": {"id": person["sp"]},
                                        "notification_type": "regular",
                                        "message": {
                                            "text": response_sent_text
                                        }
                                    }
                                send_request(payload)
                        else:
                            psych_init(db,recipient_id,message)
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
                                    db.paired_peeps.remove({"fp":person["fp"],"sp":person["sp"]})
                                    db.user_status.update_one({"user": person["sp"]}, {"$set": {"status": 0}})
                                    db.user_status.update_one({"user": person["fp"]}, {"$set": {"status": 0}})
                                    if person["fp"] == message["sender"]["id"]:
                                        reported_person =  person["sp"]
                                    else:
                                        reported_person =  person["fp"]
                                    print(reported_person)
                                    db.report.insert_one({"reported_user":reported_person,"reporting_user":message["sender"]["id"],"issue":""})
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
                            if message.get("message"):
                                print(message["message"]["text"])
                    elif status//10==3:
                        cur_speaker = ""
                        persona_id_cur = ""
                        person = db.paired_peeps.find_one({"sp": message["sender"]["id"]})
                        print(person)
                        if message.get("message"):
                            response_sent_text = message["message"]["text"]
                            if (response_sent_text=="/end"):
                                db.paired_peeps.remove({"fp":person["fp"],"sp":person["sp"]})
                                db.user_status.update_one({"user": person["sp"]}, {"$set": {"status": 0}})
                                db.user_status.update_one({"user": person["fp"]}, {"$set": {"status": 90}})
                                payload_partner = {
                                    "message": {
                                        "text": "Thank you for your time!!! "
                                    },
                                    "recipient": {"id": person["fp"]},
                                    "notification_type": "regular"
                                }
                                send_request(payload_partner)
                                payload = {
                                    "recipient": {"id": person["sp"]},
                                    "notification_type": "regular",
                                    "message": {
                                        "text": "The chat ended. Hope we could help you."
                                    },
                                }
                            else:
                                payload = {
                                        "recipient": {"id": person["fp"]},
                                        "notification_type": "regular",
                                        "message": {
                                            "text": response_sent_text
                                        }
                                    }
                            send_request(payload)    
            elif (event.get("standby")):
                handle_standby(event["standby"])
    return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"
