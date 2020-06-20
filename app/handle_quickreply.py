from .book_appointment import *

def handle_quickreply(db, recipient_id, qreply):
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
    elif message_rec["quick_reply"]["payload"] in like_replies:
            ind = like_replies.index(message_rec["quick_reply"]["payload"])
            ind_cat = "score"+str(ind)
            category_data = db.joke_categories.find({"user":recipient_id})
            score = category_data[ind][ind_cat]
            db.joke_categories.update_one({ind_cat:score},{"$inc": {ind_cat: float(20)}})
            payload = {
                "message": {"text": "Glad you liked it!"},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
    elif message_rec["quick_reply"]["payload"] in dislike_replies:
        ind = dislike_replies.index(message_rec["quick_reply"]["payload"])
        ind_cat = "score"+str(ind)
        category_data = db.joke_categories.find({"user":recipient_id})
        score = category_data[ind][ind_cat]
        db.joke_categories.update_one({ind_cat:score},{"$inc": {ind_cat: float(-20)}})
        payload = {
            "message": {"text": "I am so sorry!"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    elif message_rec["quick_reply"]["payload"].startswith(("date","time","reminder")):
        payload = book_appointment(message_rec["quick_reply"]["payload"], recipient_id, db)

    # elif message_rec["quick_reply"]["payload"].startswith("reminder"):
    #     payload = {
    #         "recipient": {"id": recipient_id},
    #         "message": {
    #             "attachment": {
    #                 "type": "template",
    #                 "payload": {
    #                     "template_type": "one_time_notif_req",
    #                     "title": 'Select "notify me" to confirm the reminder?',
    #                     "payload": message_rec["quick_reply"]["payload"],
    #                 },
    #             }
    #         },
    #     }
    else:
        payload = {
        "message": {"text": "quick_reply_invalid"},
        "recipient": {"id": recipient_id},
        "notification_type": "regular",
        }
    return payload