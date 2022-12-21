from WebUtils.PinterestAPI import topic_feed_query
from WebUtils.PinterestAPI import paged_threaded_post_responses_query
from WebUtils.PinterestAPI import clap_mutation
from WebUtils.PinterestAPI import user_profile_query
from StorageUtils.SQLite import SQLite
from JSONWrap.utils import load

import time
from random import randint

dct = load('config/WebUtils/PinterestConfig.yaml')

OUT = dct['out']
CFG = dct['cfg']
KEYWORD = dct['key']
USERNAMES = dct['usernames']
CLAPS = dct['claps']
START = dct['start']
END = dct['end']

rate = int((END - START) / CLAPS)
sigma = int(rate * 0.1)
stats = {	'claps' : 0, 'tried' : 0, 'visited' : 0, 'total' : 0}

db = SQLite(f'{OUT}/PinterestAPI.db', config=f'{CFG}/PinterestAPI.yaml')

for username in USERNAMES:
	to1 = None
	
	while True:
		print('User')
		to1, dct1 = user_profile_query(
			f'{CFG}/UserProfileQuery.curl', username, to1)
		time.sleep(1)
		
		for k,v in dct1.items():
			db.fetch(name=f'insert_{k}', params=v)
		
		t = '","'.join( [str(x[4]) for x in dct1['Post']] )
		visited = db.fetch(query=f'SELECT id FROM Visited WHERE id IN ("{t}");')
		visited = set([x[0] for x in visited])
		done = []
		
		for post in dct1['Post']:
			print('\t', 'Post')
			stats['total'] += 1
			if post[4] in visited:
				continue
			db.fetch(name='insert_Visited', params=[(post[4],int(time.time()))])
			if post[15] == 0: # without comments
				continue
			stats['visited'] += 1
			to2 = None
			
			while True:
				print('\t\t', 'Comment')
				to2, dct2 = paged_threaded_post_responses_query(
					f'{CFG}/PagedThreadedPostResponsesQuery.curl',
					url=post[13],
					to=to2
				)
				time.sleep(1)
				
				for k,v in dct2.items():
					db.fetch(name=f'insert_{k}', params=v)
				
				for comment, creator in zip(dct2['Comment'],dct2['Creator']):
					print('\t\t\t', stats)
					if creator[3] == 0: # not a member
						continue
					stats['tried'] += 1
					
					time.sleep(randint(int(rate-sigma/2), int(rate+sigma/2)))
					
					up = clap_mutation(
						f'{CFG}/ClapMutation.curl',
						url=post[13],
						target_id=comment[4]
						)
					if up == comment[1] + 1:
						db.fetch(name='insert_Visited', params=[(comment[4],int(time.time()))])
						stats['claps'] += 1
					
					cur = int(time.time()) % 86400
					if (START < END):
						if cur < START:
							print('Waiting', START - cur)
							time.sleep(START - cur)
						elif cur >= END:
							print('Waiting', START + 86400 - cur)
							time.sleep(START + 86400 - cur)
						else:
							time.sleep(randint(int(rate-sigma/2), int(rate+sigma/2)))
					else:
						if cur < START and cur >= END:
							print('Waiting', START - cur)
							time.sleep(START - cur)
						else:
							time.sleep(randint(int(rate-sigma/2), int(rate+sigma/2)))
				
				if to2 is None:
					break
		
		if to1 is None:
			break
	
del db
