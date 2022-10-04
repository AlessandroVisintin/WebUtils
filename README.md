# WebUtils
> Helper modules to work with the Web.

WebUtils contains a series of modules that helps in working with online data.


## Installation
Clone the project inside your working directory.
You can install the package locally by running pip at the root level.
```sh
pip install /path/to/root/level
```

## Usage examples
Scrape user info from Twitter.
```py
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
```
Scrape user info from Instagram.
```py

from WebUtils.InstagramScraper import InstagramScraper
from JSONWrap.utils import load


HEADERS = 'config/WebUtils/instagram/headers.yaml'
COOKIES = 'config/WebUtils/instagram/cookies.yaml'

scrape = InstagramScraper(load(COOKIES), load(HEADERS))

# get user info
h1, info = scrape.user_info('barackobama', 'unauth')

```
Get online resource or parse cURL headers.
```py

from WebUtils.utils import get, parse_curl_headers


# get online JSON
URL = 'https://jsonplaceholder.typicode.com/todos/1'
print(get(URL, ctype='json'), '\n')

# extract headers from cURL command
PATH = 'config/WebUtils/example.curl'
print(parse_curl_headers(in_path=PATH))
```
Create a stoppable sleep.
```py

from WebUtils.StoppableSleep import StoppableSleep


clock = StoppableSleep()

# CTRL-C should exit the sleep immediately
clock.sleep(5)
print('Done!')

# Can be used multiple times
clock.sleep(5)
print('Done!')

```

## Meta
Alessandro Visintin - alevise.public@gmail.com

Find me: [Twitter](https://twitter.com/analog_cs) [Medium](https://medium.com/@analog_cs)

Distributed under the MIT license. See ``LICENSE.txt``.
