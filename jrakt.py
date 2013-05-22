from config import *
from math import ceil
import re
import requests
from bs4 import BeautifulSoup


def openJinniSession():
    print 'Initializing...'
    jinni = requests.session()
    jinni.get('http://www.jinni.com')
    print 'Logging in as %s...' % username
    jinni.post('http://www.jinni.com/jinniLogin', {'user': username, 'pass': password, 'loginOverlayURL': '', 'loginSource': 'loginOverlay'})
    print 'Logged in as %s' % username
    return jinni


def getMovieLinks(page=1, viewstate=None, total_pages=None):
    links = []

    r = jinni.post('http://www.jinni.com/user/%s/ratings/' % username, data={'userRatingForm': 'userRatingForm', 'userRatingForm:j_id269': 'idx%s' % page, 'javax.faces.ViewState': viewstate})

    ratings_page = BeautifulSoup(r.text)

    if not total_pages:
        # Get last word of .scrollerText (ex. 'Showing 1 - 50 of 36'), divide
        # by 50 (number of results on one page) and get ceiling of the result
        total_pages = int(ceil(float(ratings_page.find(class_='scrollerText').string.split()[-1]) / 50))

    print 'Fetching movie links from page %s of %s' % (page, total_pages)

    for div in ratings_page(id=re.compile('ratingStrip\[\d+\]')):
        print div.span
        if div.find(id=re.compile('likelyOrNotForMeContainer\[\d+\]')).get('style') == 'display: none':
            links.append('http://www.jinni.com%s' % div.a.get('href'))

    if page < total_pages:
        viewstate = ratings_page.find(id='javax.faces.ViewState').get('value')
        links += getMovieLinks(page + 1, viewstate, total_pages)

    return links


jinni = openJinniSession()
links = getMovieLinks()
