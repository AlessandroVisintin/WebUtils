"""

Collect followers lists of the followers of a user.
The collection is limited to accounts <= 5000 followers.

"""

from WebUtils.threaded_twitter import get_followers_ids
from WebUtils.threaded_twitter import get_followers
from JSONWrap.utils import load

from pathlib import Path
from queue import Queue
from threading import Thread, Event


# user to collect
USERNAME, USERID = ('twitter',783214)
OUTPATH = 'out/WebUtils/threaded_twitter'

# load authentication	
credentials = load('config/WebUtils/TwitterAPI.yaml')

# create threads for accounts < 200 followers and < 5000 followers
end = Event()
in_200 = Queue()
in_5000 = Queue()
out_200 = Queue()
out_5000 = Queue()

apis = {
	
	200 : [
		Thread(
			target=get_followers,
			args=(v, 'user', end, in_200, out_200)
			) for k,v in credentials.items()
		],
	
	5000 : [
		Thread(
			target=get_followers_ids,
			args=(v, 'user', end, in_5000, out_5000)
			) for k,v in credentials.items()
		]
	
	}

# start threads
for t in apis[200]:
	t.start()
for t in apis[5000]:
	t.start()

# create output folder 
outpath = Path(f'{OUTPATH}')
outpath.mkdir(parents=True, exist_ok=True)

# collect
count = [0,0,0]
cursor = -1
while not cursor == 0:
	print(USERNAME, count)
	
	in_200.put( (USERNAME, cursor, 200) )
	data = out_200.get()

	out = []
	for fws in data['users']:
		print(fws['screen_name'], fws['followers_count'], end=', ')
		out.append((USERID,fws['id']))
		
		if (
				fws['protected'] or
				fws['followers_count'] == 0 or
				fws['followers_count'] > 5000
				):
			count[0] += 1
		
		elif fws['followers_count'] > 200:
			in_5000.put(( fws['screen_name'], -1, 5000 ))
			out.extend([
				(fws['id'],res) for res in out_5000.get()['ids']
				])
			count[1] += 1
		
		else:
			in_200.put(( fws['screen_name'], -1, 200 ))
			out.extend([
				(fws['id'],res['id']) for res in out_200.get()['users']
				])
			count[2] += 1
	print('\n')

	# write results
	with (outpath / USERNAME).open('a+') as f:
		for a,b in out:
			f.write(f'{a}\t{b}\n')
		f.flush()
	
	cursor = data['next_cursor']
	# write log
	with (outpath / 'log.txt').open('w') as f:
		f.write(f'{USERNAME}\t{cursor}\n')
		f.flush()

# close threads
end.set()
for t in apis[200]:
	in_200.put(None)
	t.join()
for t in apis[5000]:
	in_5000.put(None)
	t.join()
