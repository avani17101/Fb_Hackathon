from .fb_requests import *
def handle_standby(standby):
	for message in standby:
		text = message["message"]["text"]
		recipient_id = message["sender"]["id"]
		if (text=="/end"):
			take_payload = {
			"recipient":{"id":recipient_id},
			"metadata":"Giving control back to bot"
			}
			take_handover_request(take_payload)
	#print (standby)

