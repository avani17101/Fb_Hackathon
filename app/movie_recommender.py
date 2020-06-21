import imdb
from imdb import IMDb
import random
def get_movies():
    keywords = ['motivational','cheerfull','comedy']
    keyword = random.choice(keywords)
    # create an instance of the IMDb class
    ia = IMDb()
    movies = ia.get_keyword(keyword)
    print(random.choice(movies))
    return random.choice(movies)


# get_movies()