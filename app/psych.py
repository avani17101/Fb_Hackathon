from .fb_requests import send_request

def psych_send_message(text,recipient_id,message_rec,psych_id,db):
	elif message_rec["text"] == "Display schedule":
		psych_data = db.appointment.find({"therapist_id":psych_id})
		slots_list={}
		slot_dates = []
		for slot in psych_data:
			if (slot["date"] not in slot_dates):
				slot_dates.append(slot["date"])
				time_slots=[]
				slots_list[slot["date"]]=time_slots
			slots_list[slot["date"]].append(slot["time"])
		print (slots_list)
		elements_list = []
		for date in slots_list.keys():
			button_desc = []
			for time in slots_list[date]:
				button_one = {
				"type":"web_url",
				"url": "https://www.google.com/search?client=ubuntu&channel=fs&q=clock+image&ie=utf-8&oe=utf-8",
			    "title":time
			    }
				button_desc.append(button_one)
			element_desc={
			 	"title":date,
	            "image_url":"https://png.pngtree.com/thumb_back/fh260/background/20190903/pngtree-colorful-bright-smoke-texture-background-image_312909.jpg",
	            "subtitle":"Your slots for the day:",
	            "default_action": {
	              "type": "web_url",
	              "url": "https://media.gettyimages.com",
	              "webview_height_ratio": "tall",
	            },
	            "buttons":button_desc
			}
			elements_list.append(element_desc)
		print (elements_list)
		payload = {
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
                "message": {
                    "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"generic",
                        "elements": elements_list
						}
					}
				}
			}
		# payload = {
  #               "recipient": {"id": recipient_id},
  #               "notification_type": "regular",
  #               "message": {
  #                   "text": "The chat ended. We hope you feel better. Please take some time to rate your partner."
  #               },
  #               }
		send_request(payload)



