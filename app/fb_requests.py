from .config import ACCTOKEN
import requests

FB_API_URL = "https://graph.facebook.com/v7.0/me/messages"
FB_PERSONA_URL = "https://graph.facebook.com/me/personas"
FB_HANDOVER_URL = "https://graph.facebook.com/v7.0/me/pass_thread_control"
FB_TAKE_URL = "https://graph.facebook.com/v7.0/me/take_thread_control"
def send_request(payload):
    auth = {"access_token": ACCTOKEN}
    response = requests.post(FB_API_URL, params=auth, json=payload)
    print(response, response.json())
    return "success"

def send_persona_request(payload):
    auth = {"access_token": ACCTOKEN}
    response = requests.post(FB_PERSONA_URL, params=auth, json=payload)
    persona_id =  response.json()["id"]
    print ("I'm in function ",persona_id)
    return persona_id
def send_handover_request(payload):
    auth = {"access_token": ACCTOKEN}
    response = requests.post(FB_HANDOVER_URL, params=auth, json=payload)
    return "success"
def take_handover_request(payload):
    auth = {"access_token": ACCTOKEN}
    response = requests.post(FB_TAKE_URL, params=auth, json=payload)
    return "success"