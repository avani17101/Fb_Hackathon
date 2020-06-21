import json
import random
def fetch_quote():
    f = open('quotes.json',)
    quotes = json.load(f)
    print(random.choice(list(quotes[1].values())))
    return random.choice(list(quotes[1].values()))


