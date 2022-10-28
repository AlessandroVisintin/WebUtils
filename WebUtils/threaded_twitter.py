import tweepy

import time
from queue import Queue
from threading import Event


def apiv11(cred:dict, context:str) -> tweepy.API:
	"""
	
	Initiate a Twitter API v1.1 object.
	
	Args:
		cred : {
			"api_key" : ..,
			"api_secret" : ..,
			"tok_key" : ..,
			"tok_secret" : ..,
			"bearer" : ..
			}
		context : either 'app' or 'user'. Defaults to 'user'.
	
	"""
	
	auth = None
	if context == 'app':
		auth = tweepy.OAuth2BearerHandler(cred['bearer'])
	else:
		auth = tweepy.OAuth1UserHandler(
			consumer_key=cred['api_key'],
			consumer_secret=cred['api_secret'],
			access_token=cred['tok_key'],
			access_token_secret=cred['tok_secret'],
			)
	return tweepy.API(auth, parser=tweepy.parsers.JSONParser())


def apiv2(cred:dict, context:str) -> tweepy.Client:
	"""
	
	Initiate a Twitter API v2 object.
	
	Args:
		cred : {
			"api_key" : ..,
			"api_secret" : ..,
			"tok_key" : ..,
			"tok_secret" : ..,
			"bearer" : ..
			}
		context : either 'app' or 'user'. Defaults to 'user'.
	
	"""
	
	if context == 'app':
		return tweepy.Client(cred['bearer'])
	else:
		return tweepy.Client(
			consumer_key=cred['api_key'],
			consumer_secret=cred['api_secret'],
			access_token=cred['tok_key'],
			access_token_secret=cred['tok_secret'],
			)


def get_follower_ids(auth:dict, context:str, qin:Queue, qout:Queue) -> None:
	"""
	
	Worker for collecting followers IDs.
	Thread is terminated by sending None. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		qin : threaded input.
			Expects tuple({username/userid}, {cursor}, {count}).
			Max count = 5000.
		qout : threaded output.

	"""
	
	base_delta = 60
	last = time.time() - base_delta
	api = apiv11(auth, context)
	while True:
		i =  qin.get()
		if i is None:
			break
		if not (isinstance(i, tuple) and len(i) == 3 and i[2] <= 5000):
			qin.put(i)
			continue
		
		delta = last - time.time() + base_delta
		time.sleep(delta if delta > 0 else 0)
		
		try:
			data = (
				api.get_follower_ids(screen_name=i[0], cursor=i[1], count=i[2])
				if isinstance(i[1], str) else
				api.get_follower_ids(user_id=i[0], cursor=i[1], count=i[2])
				)
			qout.put(data[0])
			last = time.time()
		except tweepy.TooManyRequests:
			print('TooManyRequests')
			qin.put(i)
			reset = api.rate_limit_status()
			reset = reset['resources']['followers']['/followers/ids']['reset']
			last = reset - base_delta
		except (tweepy.NotFound, tweepy.TwitterServerError,
				tweepy.TweepyException) as e:
			print(f'TweepyError: {e}')
			qin.put(i)
			last = time.time() + 60 - base_delta


def get_friend_ids(auth:dict, context:str, qin:Queue, qout:Queue) -> None:
	"""
	
	Worker for collecting friends IDs.
	Thread is terminated by sending None. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		qin : threaded input.
			Expects tuple({username/userid}, {cursor}, {count}).
			Max count = 5000.
		qout : threaded output.

	"""
	
	base_delta = 60
	last = time.time() - base_delta
	api = apiv11(auth, context)
	while True:
		i =  qin.get()
		if i is None:
			break
		if not (isinstance(i, tuple) and len(i) == 3 and i[2] <= 5000):
			qin.put(i)
			continue
		
		delta = last - time.time() + base_delta
		time.sleep(delta if delta > 0 else 0)
		
		try:
			data = (
				api.get_friend_ids(screen_name=i[0], cursor=i[1], count=i[2])
				if isinstance(i[1], str) else
				api.get_friend_ids(user_id=i[0], cursor=i[1], count=i[2])
				)
			qout.put(data[0])
			last = time.time()
		except tweepy.TooManyRequests:
			print('TooManyRequests')
			qin.put(i)
			reset = api.rate_limit_status()
			reset = reset['resources']['followers']['/friends/ids']['reset']
			last = reset - base_delta
		except (tweepy.NotFound, tweepy.TwitterServerError,
				tweepy.TweepyException) as e:
			print(f'TweepyError: {e}')
			qin.put(i)
			last = time.time()  + 60 - base_delta


def get_followers(auth:dict, context:str, qin:Queue, qout:Queue) -> None:
	"""
	
	Worker for collecting followers user objects.
	Thread is terminated by sending None and. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		qin : threaded input.
			Expects tuple({username/userid}, {cursor}, {count}).
			Max count = 200.
		qout : threaded output.

	"""

	base_delta = 60
	last = time.time() - base_delta
	api = apiv11(auth, context)
	while True:
		i =  qin.get()
		if i is None:
			break
		if not (isinstance(i, tuple) and len(i) == 3 and i[2] <= 200):
			qin.put(i)
			continue
		
		delta = last - time.time() + base_delta
		time.sleep(delta if delta > 0 else 0)

		try:
			data = (
				api.get_followers(screen_name=i[0], cursor=i[1], count=i[2])
				if isinstance(i[1], str) else
				api.get_followers(user_id=i[0], cursor=i[1], count=i[2])
				)
			qout.put(data[0])
			last = time.time()
		except tweepy.TooManyRequests:
			print('TooManyRequests')
			qin.put(i)
			reset = api.rate_limit_status()
			reset = reset['resources']['followers']['/followers/list']['reset']
			last = reset - base_delta
		except (tweepy.NotFound, tweepy.TwitterServerError,
				tweepy.TweepyException) as e:
			print(f'TweepyError: {e}')
			qin.put(i)
			last = time.time() + 60 - base_delta


def get_friends(auth:dict, context:str, qin:Queue, qout:Queue) -> None:
	"""
	
	Worker for collecting friends user objects.
	Thread is terminated by sending None. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		qin : threaded input.
			Expects tuple({username/userid}, {cursor}, {count}).
			Max count = 200.
		qout : threaded output.

	"""
		
	base_delta = 60
	last = time.time() - base_delta
	api = apiv11(auth, context)
	while True:
		i =  qin.get()
		if i is None:
			break
		if not (isinstance(i, tuple) and len(i) == 3 and i[2] <= 200):
			qin.put(i)
			continue
		
		delta = last - time.time() + base_delta
		time.sleep(delta if delta > 0 else 0)

		try:
			data = (
				api.get_friends(screen_name=i[0], cursor=i[1], count=i[2])
				if isinstance(i[1], str) else
				api.get_friends(user_id=i[0], cursor=i[1], count=i[2])
				)
			qout.put(data[0])
			last = time.time()
		except tweepy.TooManyRequests:
			print('TooManyRequests')
			qin.put(i)
			reset = api.rate_limit_status()
			reset = reset['resources']['followers']['/friends/list']['reset']
			last = reset - base_delta
		except (tweepy.NotFound, tweepy.TwitterServerError,
				tweepy.TweepyException) as e:
			print(f'TweepyError: {e}')
			qin.put(i)
			last = time.time() + 60 - base_delta


def lookup_users(auth:dict, context:str, qin:Queue, qout:Queue) -> None:
	"""
	
	Worker for collecting user objects.
	Thread is terminated by sending None. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		qin : threaded input. 
			Expects either list(userid,...) or list(username,...).
			Userids are integers, usernames are strings.
			Max len of list = 100.
		qout : threaded output.

	"""

	base_delta = 1
	last = time.time() - base_delta
	api = apiv11(auth, context)
	while True:
		i =  qin.get()
		if i is None:
			break
		if not (isinstance(i, list) and len(i) > 0):
			qin.put(i)
			continue
		
		delta = last - time.time() + base_delta
		time.sleep(delta if delta > 0 else 0)

		try:
			data = (
				api.lookup_users(screen_name=i) if isinstance(i[0], str) else
				api.lookup_users(user_id=i)
				)
			qout.put(data)
			last = time.time()
		except tweepy.NotFound:
			print('NotFound')
			if len(i) > 1:
				mid = int(len(i) / 2)
				qin.put(i[:mid])
				qin.put(i[mid:])
			else:
				qout.put(None)
			last = time.time() + 60 - base_delta
		except tweepy.TooManyRequests:
			print('TooManyRequests')
			qin.put(i)
			reset = api.rate_limit_status()
			reset = reset['resources']['followers']['/users/lookup']['reset']
			last = reset - base_delta
		except (tweepy.TwitterServerError, tweepy.TweepyException) as e:
			print(f'TweepyError: {e}')
			qin.put(i)
			last = time.time() + 60 - base_delta
	