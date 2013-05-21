from config import *
import re
import requests
from bs4 import BeautifulSoup

s = requests.session()
s.get('https://www.jinni.com')
s.post('https://www.jinni.com/jinniLogin', {'user': username, 'pass': password, 'loginOverlayURL': '', 'loginSource': 'loginOverlay'})

movielinks = []
def getRatingsPage(page=2):
    r = s.post('https://www.jinni.com/user/%s/ratings/' % username, {'userRatingForm': 'userRatingForm', 'userRatingForm:j_id269': 'idx%s' % page, 'userRatingForm:j_id269idx%s' % page: 'userRatingForm:j_id269idx%s' % page})


    ratings_page = BeautifulSoup(r.text)

    for div in ratings_page(id=re.compile('ratingStrip\[\d+\]')):
        movielinks.append('https://www.jinni.com%s' % div.a.get('href'))

    if ratings_page.find(class_='next_rev'):
        print ratings_page.find(class_='activePage').string

getRatingsPage()
print movielinks
