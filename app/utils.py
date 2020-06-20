import requests
from .quick_replies import replies
def jokes_util(recipient_id,db):
	#category = db.joke_categories.aggregate({"$group" : {"_id": null, max: {"$max" : "$score" }}})
	#category = db.joke_categories.find()
	joke_c = db.user_status.find_one({"user":recipient_id})
	if (joke_c["joke_calls"]<=4):
		category_data = db.joke_categories.find_one({"joke_tag":0})
		max_cat = category_data["category"]
		db.user_status.update_one({"user":recipient_id},{"$inc":{"joke_calls":int(1)}})
		db.joke_categories.update({"category":max_cat},{"$inc":{"score":float(40)}})
		db.joke_categories.update_one({"category":max_cat},{"$set": {"joke_tag": 2}})
	else:
		max_score = 0
		max_cat = ""
		joke = ""
		category_data = db.joke_categories.find({"joke_tag":1})
		for i in category_data:
			cat_score = i["score"]
			if (cat_score>max_score):
				max_score = cat_score
				max_cat = i["category"]
	if (max_cat=="chuck"):
		url = "http://api.icndb.com/jokes/random"
		resp = requests.get(url)
		resp.encoding = "utf-8"
		data = resp.json()
		joke = data["value"]["joke"]
	elif (max_cat=="programming"):
		url = "https://jokeapi-v2.p.rapidapi.com/joke/Dark"
		querystring = {"format":"json","blacklistFlags":"nsfw","idRange":"0-150","type":"single"}

		headers = {
		    'x-rapidapi-host': "jokeapi-v2.p.rapidapi.com",
		    'x-rapidapi-key': "a6b6e74c76msh2bf08617fc0ad50p18382ajsne3b8b2aa7d59"
		    }

		response = requests.request("GET", url, headers=headers, params=querystring)
		joke = response.json()["joke"]
	elif (max_cat=="yomama"):
		url = "https://api.yomomma.info"
		response = requests.request("GET", url)
		print (response)
		joke = response.json()["joke"]
	elif (max_cat=="dad"):
		headers = {
		    'Accept': 'application/json',
		}
		response = requests.get('https://icanhazdadjoke.com', headers=headers)
		print (response.json())
		joke = response.json()["joke"]
	payload = {
	"message": {"text": joke,"quick_replies":replies["jokes"]},
    "recipient": {"id": recipient_id},
    "notification_type": "regular",
	}
	return payload