from config import *
from math import ceil
import re
import requests
import json
import hashlib
from bs4 import BeautifulSoup


class Title:
    def __init__(self, link, rating):
        self.link = link
        self.rating = rating
        self.imdbid = None
        self.titletype = None  # 'movie' or 'show'
        self.timestamp = None

        self.fixZeroRating()

    def fixZeroRating(self):
        if self.rating == 0:
            self.rating == 1

    def getIMDbID(self):
        print 'Fetching IMDb ID of %s' % self.link
        movie_page = BeautifulSoup(j.get(self.link).text)
        imdbidindex = int(str(movie_page).find('http://www.imdb.com/title/')) + 26
        self.imdbid = str(movie_page)[imdbidindex:imdbidindex+9]

    def setType(self, titletype):
        self.titletype = titletype


def openJinniSession():
    print 'Initializing...'
    j = requests.session()
    j.get('http://www.jinni.com')
    print 'Logging in as %s...' % jinni['username']
    j.post('http://www.jinni.com/jinniLogin', {'user': jinni['username'], 'pass': jinni['password'], 'loginOverlayURL': '', 'loginSource': 'loginOverlay'})
    print 'Logged in as %s' % jinni['username']
    return j


def getLinkRatings(page=1, viewstate=None, total_pages=None):
    titles = []
    r = j.post('http://www.jinni.com/user/%s/ratings/' % jinni['username'], data={'userRatingForm': 'userRatingForm', 'userRatingForm:j_id269': 'idx%s' % page, 'javax.faces.ViewState': viewstate})

    ratings_page = BeautifulSoup(r.text)

    if not total_pages:
        # Get last word of .scrollerText (ex. 'Showing 1 - 50 of 36'), divide
        # by 50 (number of results on one page) and get ceiling of the result
        total_pages = int(ceil(float(ratings_page.find(class_='scrollerText').string.split()[-1]) / 50))

    print 'Fetching movie links from page %s of %s' % (page, total_pages)

    for div in ratings_page(id=re.compile('ratingStrip\[\d+\]')):
        if div.find(id=re.compile('likelyOrNotForMeContainer\[\d+\]')).get('style') == 'display: none':
            link = 'http://www.jinni.com%s' % div.a.get('href')
            rating = div.find(class_='digitRate').string[:-10]
            # TODO: timestamp
            titles.append(Title(link, rating))

    if page < total_pages:
        viewstate = ratings_page.find(id='javax.faces.ViewState').get('value')
        titles += getLinkRatings(page + 1, viewstate, total_pages)

    return titles


def submitSeenMovies(titles):
    jsondata = {'username': trakt['username'],
                'password': hashlib.sha1(trakt['password']).hexdigest(),
                'movies': [{'imdb_id': title.imdbid} for title in titles if title.titletype == 'movie' or not title.titletype]}
    r = requests.post('http://api.trakt.tv/movie/seen/%s' % (trakt['api_key']), json.dumps(jsondata))
    print r.text

    skipped = [entry['imdb_id'] for entry in r.json()['skipped_movies']]
    [title.setType('show') if title.imdbid in skipped else title.setType('movie') for title in titles]


def submitSeenShows(titles):
    for title in titles:
        if title.titletype == 'show':
            jsondata = {'username': trakt['username'],
                        'password': hashlib.sha1(trakt['password']).hexdigest(),
                        'imdb_id': title.imdbid}
            r = requests.post('http://api.trakt.tv/show/seen/%s' % (trakt['api_key']), json.dumps(jsondata))
            print r.text


def main():
    global j
    j = openJinniSession()
    titles = getLinkRatings()

    for title in titles:
        title.getIMDbID()

    submitSeenMovies(titles)
    submitSeenShows(titles)

if __name__ == '__main__':
    main()
