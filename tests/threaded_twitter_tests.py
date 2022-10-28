from WebUtils.threaded_twitter import get_friend_ids
from WebUtils.threaded_twitter import get_friends
from WebUtils.threaded_twitter import get_follower_ids
from WebUtils.threaded_twitter import get_followers
from WebUtils.threaded_twitter import lookup_users
from JSONWrap.utils import load

from queue import Queue
from threading import Thread


credentials = load('config/WebUtils/twitterapi_cred.yaml')

qin = Queue()
qout = Queue()

for k,v in credentials.items():
	print('get_friend_ids: should take 60s..')
	t = Thread(target=get_friend_ids, args=(v, 'user', qin, qout))
	t.start()		
	qin.put(('twitter',-1,100))
	qout.get()
	qin.put(('twitter',-1,100))
	fwg_i = qout.get()
	qin.put(None)
	t.join()
	print('get_friends: should take 60s..')
	t = Thread(target=get_friends, args=(v, 'user', qin, qout))
	t.start()		
	qin.put(('twitter',-1,100))
	qout.get()
	qin.put(('twitter',-1,100))
	fwg = qout.get()
	qin.put(None)
	t.join()
	print('get_follower_ids: should take 60s..')
	t = Thread(target=get_follower_ids, args=(v, 'user', qin, qout))
	t.start()		
	qin.put(('twitter',-1,100))
	qout.get()
	qin.put(('twitter',-1,100))
	fws_i = qout.get()
	qin.put(None)
	t.join()
	print('get_followers: should take 60s..')
	t = Thread(target=get_followers, args=(v, 'user', qin, qout))
	t.start()		
	qin.put(('twitter',-1,100))
	qout.get()
	qin.put(('twitter',-1,100))
	fws = qout.get()
	qin.put(None)
	t.join()
	print('lookup_users: should take 1s..')
	t = Thread(target=lookup_users, args=(v, 'user', qin, qout))
	t.start()		
	qin.put(['twitter'])
	qout.get()
	qin.put(['twitter'])
	usr = qout.get()
	qin.put(None)
	t.join()
	
	break
