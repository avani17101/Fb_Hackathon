from .book_appointment import *
def handle_quickreply(recipient_id, qreply):
    if qreply == "red":
        payload = {
            "message": {"text": "You chose red"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    elif qreply == "green":
        payload = {
            "message": {"text": "You chose green"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    elif qreply == "good":
        payload = {
            "message": {"text": "We look forward to it!"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    elif qreply == "medium":
        payload = {
            "message": {"text": "Thanks"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    elif qreply == "bad":
        payload = {
            "message": {"text": "We promise to be better next time"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    elif qreply.startswith(("date","time","reminder")):
        payload = book_appointment(qreply, recipient_id, db)

    elif qreply.startswith("reminder"):
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "one_time_notif_req",
                        "title": 'Select "notify me" to confirm the reminder?',
                        "payload": qreply,
                    },
                }
            },
        }
    return payload