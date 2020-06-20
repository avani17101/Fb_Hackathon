from .fb_requests import *
from .random_message import *
from .send_message import *

def handle_normal_message(db,recipient_id,message):
    # Facebook Messenger ID for user so we know where to send response back to
    if (message["message"].get("attachments")):
        print("Attachment not supported")
    if message["message"].get("text"):
        response_sent_text = get_message()
        send_message(
            db, recipient_id, response_sent_text, message["message"]
        )