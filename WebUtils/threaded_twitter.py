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


def get_followers_ids(auth:dict, context:str, 
						end:Event, queue_in:Queue, queue_out:Queue) -> None:
	"""
	
	Worker for collecting followers IDs.
	Thread is terminated by sending None and setting end event. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		end : exit flag.
		queue_in : threaded input. Expects tuple(username, cursor, count).
			Min count = 201, max count = 5000
		queue_out : threaded output.

	"""
	
	api = apiv11(auth, context)
	while not end.is_set():
		i =  queue_in.get()
		if i is None:
			break
		try:
			if i[2] <= 200 or i[2] > 5000:
				queue_in.put(i)
				continue
			data = api.get_follower_ids(
				screen_name=i[0], cursor=i[1], count=i[2])
			queue_out.put(data[0])
			end.wait(60)
		except IndexError:
			print(f'IndexError {i[0]}')
			queue_in.put(i)
		except tweepy.NotFound:
			print(f'NotFound {i[0]}')
			queue_in.put(i)
			end.wait(60)
		except tweepy.TooManyRequests:
			print(f'TooManyRequests {i[0]}')
			queue_in.put(i)
			reset = (api.rate_limit_status()
				['resources']['followers']['/followers/ids']['reset'])
			end.wait(reset - time.time())
		except tweepy.TwitterServerError:
			print(f'ServerError {i[0]}')
			queue_in.put(i)
			end.wait(60)


def get_followers(auth:dict, context:str, 
						end:Event, queue_in:Queue, queue_out:Queue) -> None:
	"""
	
	Worker for collecting followers user objects.
	Thread is terminated by sending None and setting end event. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		end : exit flag.
		queue_in : threaded input. Expects tuple(username, cursor, count).
			Max count = 200
		queue_out : threaded output.

	"""
	
	api = apiv11(auth, context)
	while not end.is_set():
		i =  queue_in.get()
		if i is None:
			break
		try:
			if i[2] <= 0  or i[2] > 200:
				queue_in.put(i)
				continue
			data = api.get_followers(
				screen_name=i[0], cursor=i[1], count=i[2])
			queue_out.put(data[0])
			end.wait(60)
		except IndexError:
			print(f'IndexError {i[0]}')
			queue_in.put(i)
		except tweepy.NotFound:
			print(f'NotFound {i[0]}')
			queue_in.put(i)
			end.wait(60)
		except tweepy.TooManyRequests:
			print(f'TooManyRequests {i[0]}')
			queue_in.put(i)
			reset = (api.rate_limit_status()
				['resources']['followers']['/followers/list']['reset'])
			end.wait(reset - time.time())
		except tweepy.TwitterServerError:
			print(f'ServerError {i[0]}')
			queue_in.put(i)
			end.wait(60)


def lookup_users(auth:dict, context:str, 
						end:Event, queue_in:Queue, queue_out:Queue) -> None:
	"""
	
	Worker for collecting followers user objects.
	Thread is terminated by sending None and setting end event. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		end : exit flag.
		queue_in : threaded input. 
			Expects either list(userid,...) or list(username,...).
			Userids are integers, usernames are strings. Max len of list = 100
		queue_out : threaded output.

	"""
	
	api = apiv11(auth, context)
	while not end.is_set():
		i =  queue_in.get()
		if i is None:
			break
		try:
			if isinstance(i[0], str):
				data = api.lookup_users(screen_name=i)
				queue_out.put(data)
			else:
				data = api.lookup_users(user_id=i)
				queue_out.put(data)
			end.wait(1)
		except tweepy.NotFound:
			print(f'NotFound {i[0]}')
			queue_in.put(i)
			end.wait(60)
		except tweepy.TooManyRequests:
			print(f'TooManyRequests {i[0]}')
			queue_in.put(i)
			reset = (api.rate_limit_status()
				['resources']['users']['/users/lookup']['reset'])
			end.wait(reset - time.time())
		except tweepy.TwitterServerError:
			print(f'ServerError {i[0]}')
			queue_in.put(i)
			end.wait(60)


def get_users_followers(auth:dict, context:str, 
						end:Event, queue_in:Queue, queue_out:Queue) -> None:
	"""
	
	Worker for collecting followers user objects (API v2).
	Thread is terminated by sending None and setting end event. 
	
	Args:
		auth : see apiv11() for reference.
		context : see apiv11() for reference.
		end : exit flag.
		queue_in : threaded input.
			Expects tuple(userid, cursor, max_results(<=1000), ).
		queue_out : threaded output.

	"""

	api = apiv2(auth, context)
	while not end.is_set():
		i =  queue_in.get()
		if i is None:
			break
		try:
			data = api.get_users_followers(
				id=i[0],
				pagination_token=i[1],
				max_results=i[2],
				user_fields=[
					'created_at', 'description', 'entities', 'id',
					'location', 'name', 'pinned_tweet_id', 'profile_image_url',
					'protected', 'public_metrics', 'url', 'username', 'verified',
					'withheld'
					]
				)
			queue_out.put(data[0])
			end.wait(60)
		except tweepy.TooManyRequests:
			print('Reset: ', i)
			queue_in.put(i)
			reset = (api.rate_limit_status()
				['resources']['followers']['/followers/list']['reset'])
			end.wait(reset - time.time())
		except tweepy.TwitterServerError:
			print('Server: ', i)
			queue_in.put(i)
			end.wait(60)

	