from config import *
import re
import requests
from bs4 import BeautifulSoup

s = requests.session()
s.get('http://www.jinni.com')
s.post('http://www.jinni.com/jinniLogin', {'user': username, 'pass': password, 'loginOverlayURL': '', 'loginSource': 'loginOverlay'})

movielinks = []


def getRatingsPage(page=1, viewstate=None):
    r = s.post('http://www.jinni.com/user/%s/ratings/' % username, data={'userRatingForm': 'userRatingForm', 'userRatingForm:j_id269': 'idx%s' % page, 'javax.faces.ViewState': viewstate})

    ratings_page = BeautifulSoup(r.text)

    # Total pages are calculated like so:
    # Get number from last word of .scrollerText (ex. 'Showing 1 - 50 of 361')
    # Divide them by 50 (the number of results on one page)
    # Convert result to integer, which will always round down
    # Add one, sicne we wanted to round it up
    total_pages = int(float(ratings_page.find(class_='scrollerText').string.split()[-1]) / 50) + 1
    print 'Fetching movie links from page %s of %s' % (page, total_pages)

    for div in ratings_page(id=re.compile('ratingStrip\[\d+\]')):
        movielinks.append('http://www.jinni.com%s' % div.a.get('href'))
    if ratings_page.find(class_='next_rev'):
        viewstate = ratings_page.find(id='javax.faces.ViewState').get('value')
        getRatingsPage(page + 1, viewstate)

getRatingsPage()
print movielinks
