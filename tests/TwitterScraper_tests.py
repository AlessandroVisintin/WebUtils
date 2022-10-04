from JSONWrap.utils import load
from WebUtils.TwitterScraper import TwitterScraper


HEADERS = 'config/WebUtils/twitter/headers.yaml'
COOKIES = 'config/WebUtils/twitter/cookies.yaml'
ENDPOINTS = 'config/WebUtils/twitter/endpoints.yaml'

scrape = TwitterScraper(load(COOKIES), load(HEADERS), load(ENDPOINTS))

# UserInfo
h1, info = scrape.user_info('BarackObama', 'margaret')

# Followers
h2, followers = scrape.followers('BarackObama', '813286', 'margaret')
