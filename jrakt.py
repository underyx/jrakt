from config import *
import requests
from bs4 import BeautifulSoup

s = requests.session()
s.get('https://www.jinni.com')
s.post('https://www.jinni.com/jinniLogin', data={'user': username, 'pass': password, 'loginOverlayURL': '', 'loginSource': 'loginOverlay'})
r = s.get('http://www.jinni.com/user/%s/ratings/' % username)
print r.text
