import datetime

def generate_app_slots(cur_slots,available_slots):
    slots_arr = []
    for i in range(len(cur_slots)):
        if (available_slots[i]):
            slot_dict =  {
                    "content_type":"text",
                    "title":str(cur_slots[i]),
                    "payload":str("appointment "+str(cur_slots[i])),
                    "image_url":"https://i.pinimg.com/736x/af/3e/d0/af3ed088eb35793c077894f48f383e84.jpg"
                }
        slots_arr.append(slot_dict)
    return slots_arr
def generate_reminder_slots(app_time):
    t = datetime.datetime.strptime("10","%M")
    delta = datetime.timedelta(hours=0, minutes=t.minute, seconds=0)
    reminders = []
    for i in range(1,4):
        temp_dict = {}
        temp_time = app_time - i*delta
        temp_time_str = temp_time.strftime("%H:%M")
        temp_dict['content_type'] = "text"
        temp_dict['title'] = temp_time_str
        temp_dict['payload'] = "reminder " + temp_time_str+" "+app_time.strftime("%H:%M")
        temp_dict["image_url"]="https://i.pinimg.com/736x/af/3e/d0/af3ed088eb35793c077894f48f383e84.jpg"
        reminders.append(temp_dict)
    return reminders    

replies = {
	"color": 
	[
            {
                "content_type":"text",
                "title":"Red",
                "payload":"red",
                "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
            },{
                "content_type":"text",
                "title":"Green",
                "payload":"green",
                "image_url":"https://lh3.googleusercontent.com/proxy/4thAzIZQcMhIFwcHQbN6j6OwzoyC-UyHmtxXCn-t5fOMgzZd7oAy4SAfSFMSZDcw1aBjSotVXnw2HDg3v6JKFqahdqu77yFtcqKPJ8iIFWAYLw"
            }
    ],
    "end_rating": 
    [
            {
                "content_type":"text",
                "title":"Would chat again",
                "payload":"good",
                "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
            },{
                "content_type":"text",
                "title":"Was okay",
                "payload":"medium",
                "image_url":"https://lh3.googleusercontent.com/proxy/4thAzIZQcMhIFwcHQbN6j6OwzoyC-UyHmtxXCn-t5fOMgzZd7oAy4SAfSFMSZDcw1aBjSotVXnw2HDg3v6JKFqahdqu77yFtcqKPJ8iIFWAYLw"
            },{
                "content_type":"text",
                "title":"Didn't help",
                "payload":"bad",
                "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
            }
    ],
    "report_options": 
    [
            {
                "content_type":"text",
                "title":"Sexual harassment/bullying",
                "payload":"bully",
                "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
            },{
                "content_type":"text",
                "title":"Rude/Insensitive",
                "payload":"rude",
                "image_url":"https://lh3.googleusercontent.com/proxy/4thAzIZQcMhIFwcHQbN6j6OwzoyC-UyHmtxXCn-t5fOMgzZd7oAy4SAfSFMSZDcw1aBjSotVXnw2HDg3v6JKFqahdqu77yFtcqKPJ8iIFWAYLw"
            },{
                "content_type":"text",
                "title":"Prankster/troll",
                "payload":"troll",
                "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
            }
    ]
}