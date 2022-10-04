from WebUtils.InstagramScraper import InstagramScraper
from JSONWrap.utils import load


HEADERS = 'config/WebUtils/instagram/headers.yaml'
COOKIES = 'config/WebUtils/instagram/cookies.yaml'

scrape = InstagramScraper(load(COOKIES), load(HEADERS))

# get user info
h1, info = scrape.user_info('barackobama', 'unauth')
