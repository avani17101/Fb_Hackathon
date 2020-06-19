import datetime

def generate_slots(cur_slots,selected_date):
    slots_arr = []
    for i in cur_slots:
        slot_dict =  {
                "content_type":"text",
                "title":str(i),
                "payload":str("time "+selected_date +" "+str(i)),
                "image_url":"https://i.pinimg.com/736x/af/3e/d0/af3ed088eb35793c077894f48f383e84.jpg"
            }
        slots_arr.append(slot_dict)
    return slots_arr

def generate_reminder_slots(app_time, selected_date):
    t = datetime.datetime.strptime("10","%M")
    delta = datetime.timedelta(hours=0, minutes=t.minute, seconds=0)
    reminders = []
    for i in range(1,4):
        temp_dict = {}
        temp_time = app_time - i*delta
        temp_time_str = temp_time.strftime("%H:%M")
        temp_dict['content_type'] = "text"
        temp_dict['title'] = temp_time_str
        temp_dict['payload'] = "reminder "+ selected_date +" " + temp_time_str+" "+app_time.strftime("%H:%M")
        temp_dict["image_url"]="https://i.pinimg.com/736x/af/3e/d0/af3ed088eb35793c077894f48f383e84.jpg"
        reminders.append(temp_dict)
    return reminders

def generate_dates(dates):
    dates_arr = []
    for i in dates:
        date_dict = {
            "content_type":"text",
            "title":str(i),
            "payload":str("date "+str(i)),
            "image_url":"https://cdn4.iconfinder.com/data/icons/small-n-flat/24/calendar-512.png"
        }
        dates_arr.append(date_dict)
    return dates_arr

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
    ]
}