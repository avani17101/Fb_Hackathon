from .main import cur_slots,available_slots
def generate_slots(cur_slots,available_slots):
    slots_arr = []
    for i in range(len(cur_slots)):
        if (available_slots[i]):
            slot_dict =  {
                    "content_type":"text",
                    "title":str(cur_slots[i]),
                    "payload":str("appointment "+str(cur_slots[i])),
                    "image_url":"https://images-eu.ssl-images-amazon.com/images/I/31oIZDvTgFL._SY300_QL70_ML2_.jpg"
                }
        slots_arr.append(slot_dict)
    return slots_arr
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
    "time_slots": generate_slots(cur_slots,available_slots)
}