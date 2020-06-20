from wit import Wit
from config import WIT_SERVER_ACCESS_TOKEN
access_token = WIT_SERVER_ACCESS_TOKEN
client = Wit(access_token = access_token)

def wit_response(message_text):
    resp = client.message(message_text)
    entity = None
    value = None
    try:
        entity = list(resp['entities'])[0]
        value = resp['entities'][entity][0]['value']
    except:
        pass
    return(entity, value)

print(wit_response("I am happyyy"))
# import requests

# headers = {
#     'Authorization': 'access_token',
#     'Content-Type': 'application/json',
# }

# data = '{"doc":"I feel great",\n       "id":"Mood",\n       "values":[{"value":"happy",\n                  "expressions":["great"]}]}'

# response = requests.post('http://curl', headers=headers, data=data)


