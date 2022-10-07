"""

Perform a simple request.

"""

from WebUtils.threaded_twitter import apiv11
from JSONWrap.utils import load


# load authentication	
credentials = load('config/WebUtils/twitterapi_cred.yaml')

# account
USERNAME = 'twitter'

# get API
key = list(credentials.keys())[0]
api = apiv11(credentials[key], 'user')

# collect
data = api.get_followers(screen_name=USERNAME)
rates = api.rate_limit_status()
