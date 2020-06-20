from .fb_requests import *
from .random_message import *
from .book_appointment import *
from .talk_to_someone import *
from .handle_quickreply import *
from .quick_replies import *
from .utils import *

def send_message(db, recipient_id, text, message_rec):
    # sends user the text message provided via input response parameter
    """Send a response to Facebook"""
    if message_rec["text"] == "Talk to someone":
        payload = talk_to_someone(recipient_id, db)
    elif message_rec["text"] == "Book an appointment":
        payload = book_appointment("", recipient_id, db)
    elif message_rec["text"] == "Get a joke":
        payload = jokes_util(recipient_id,db)
    elif message_rec["text"] == "color":
        payload = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": "Pick a color:", "quick_replies": replies["color"]},
        }
    elif message_rec["text"] == "Get a joke":
        payload = jokes_util(recipient_id,db)
    elif message_rec.get("quick_reply"):
        payload = handle_quickreply(db, recipient_id, message_rec["quick_reply"]["payload"])
    else:
        payload = {
            "message": {"text": text},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
    send_request(payload)