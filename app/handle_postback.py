from .fb_requests import *
from .send_message import *

def handle_postback(db, recipient_id, postback):
    payload = postback["payload"]
    temp_dict = {}
    temp_dict["text"] = ""
    if payload in ['harass', 'rude', 'troll']:
        db.user_status.update_one({"user": recipient_id}, {"$set": {"status": 11}})
        send_message(db, recipient_id, "We are putting you through live chat with one of the admins. Explain your isssue so that we can take necessary steps.", temp_dict)
        handover_payload = {
            "target_app_id": 263902037430900,
            "recipient":{"id":recipient_id},
            "metadata": "Redirecting to a live agent..."
        }
        db.report.update_one({"reporting_user":recipient_id},{"$set": {"issue": payload}})
        send_handover_request(handover_payload)