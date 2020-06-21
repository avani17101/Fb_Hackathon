from .fb_requests import *
from .send_message import *
def handle_optin(db, recipient_id, optin):
    payload = optin["payload"]
    notif_token = optin["one_time_notif_token"]
    temp_dict = {}
    temp_dict["text"] = ""
    if payload == "notif":
        send_message(
            db,
            recipient_id,
            "One time notif token: " + str(optin["one_time_notif_token"]),
            temp_dict,
        )
    elif payload.startswith("reminder"):
        payload_list = payload.split(" ")
        one_time_notif_dict = {
            "app_time": payload_list[3],
            "notif_time": payload_list[2],
            "date" : payload_list[1],
            "notif_token": optin["one_time_notif_token"],
        }
        db.one_time_notif.insert_one(one_time_notif_dict)
        send_message(
            db, recipient_id, "You will be notified at " + payload_list[2]+ " on "+payload_list[1], temp_dict,
        )