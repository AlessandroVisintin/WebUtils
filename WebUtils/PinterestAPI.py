from WebUtils.utils import parse_curl
from WebUtils.utils import rreq

from urllib.parse import urlparse


def parse_creator(d:dict) -> tuple:
		"""
		"""
		return (
			d['bio'],
			d['id'],
			d['isAuroraVisible'] if 'isAuroraVisible' in d else None,
			d['mediumMemberAt'],
			d['name'],
			d['socialStats']['followersCount'] if 'socialStats' in d and 'followersCount' in d['socialStats'] else -1,
			d['socialStats']['followingCount'] if 'socialStats' in d and 'followingCount' in d['socialStats'] else -1,
			d['twitterScreenName'] if 'twitterScreenName' in d else None,
			d['username']
			)


def parse_collection(d:dict) -> tuple:
		"""
		"""
		return (
			d['creator']['id'] if 'creator' in d else None,
			d['domain'],
			d['id'],
			d['isAuroraEligible'] if 'isAuroraEligible' in d else None,
			d['isAuroraVisible'] if 'isAuroraVisible' in d else None,
			d['name'],
			d['slug'],
			-1 #subscribers
			)


def parse_post(d:dict) -> tuple:
	"""
	"""
	return (
		d['allowResponses'] if 'allowResponses' in d else None,
		d['clapCount'] if 'clapCount' in d else -1,
		d['collection']['id'] if d['collection'] is not None else None,
		d['creator']['id'] if 'creator' in d else None,
		d['id'],
		d['isAuthorNewsletter'] if 'isAuthorNewsletter' in d else None,
		d['isLimitedState'] if 'isLimitedState' in d else None,
		d['isLocked'] if 'isLocked' in d else None,
		d['isNewsletter'] if 'isNewsletter' in d else None,
		d['isPublished'] if 'isPublished' in d else None,
		d['isSeries'] if 'isSeries' in d else None,
		d['isShortform'] if 'isShortform' in d else None,
		d['latestPublishedAt'],
		d['mediumUrl'],
		d['pendingCollection']['id'] if d['pendingCollection'] is not None else None,
		d['postResponses']['count'],
		d['readingTime'],
		d['responseDistribution'] if 'responseDistribution' in d else None,
		d['statusForCollection'] if 'statusForCollection' in d else None,
		d['title'],
		d['uniqueSlug'],
		d['visibility'] if 'visibility' in d else None,
		d['voterCount'] if 'voterCount' in d else -1
		)


def parse_comment(d:dict, post_id:str) -> tuple:
	"""
	"""
	return (
		d['allowResponses'] if 'allowResponses' in d else None,
		d['clapCount'] if 'clapCount' in d else -1,
		d['collection']['id'] if d['collection'] is not None else None,
		d['creator']['id'] if 'creator' in d else None,
		d['id'],
		d['isLimitedState'] if 'isLimitedState' in d else None,
		d['isPublished'] if 'isPublished' in d else None,
		d['latestPublishedAt'],
		d['mediumUrl'],
		post_id,
		d['postResponses']['count'],
		d['responseDistribution'] if 'responseDistribution' in d else None,
		d['responsesCount'] if 'responsesCount' in d else None,
		d['title'],
		d['visibility'] if 'visibility' in d else None,
		d['voterCount'] if 'voterCount' in d else -1,
		)


def topic_feed_query(cfg:str, tag_slug:str, to:int=None):
	
	cfg = parse_curl(in_path=cfg)
	
	cfg['headers']['medium-frontend-path'] = f'/tag/{tag_slug}'
	cfg['headers']['referer'] = f'https://medium.com/tag/{tag_slug}'
	cfg['data'][0]['variables']['tagSlug'] = tag_slug
	cfg['data'][0]['variables']['paging']['to'] = to
	
	_, _, data = rreq(
		cfg['url'],
		'post',
		ctype='json',
		cookies=cfg['cookies'],
		headers=cfg['headers'],
		json=cfg['data'],
		http2=True,
		max_retries=5,
		sleep=60
		)
	
	return None, data
	
	data = data[0]['data']['tagFeed']
	out = {'Collection' : [], 'Creator' : [], 'Tags' : [], 'Post' : []}
	for item in data['items']:
		item = item['post']
		if item['collection'] is not None:
			out['Collection'].append(parse_collection(item['collection']))
		if item['pendingCollection'] is not None:
			out['Collection'].append(parse_collection(item['pendingCollection']))
		out['Creator'].append(parse_creator(item['creator']))
		out['Tags'].extend([
			(item['id'], t['displayTitle'], t['id'], t['normalizedTagSlug'])
			for t in item['tags']])
		out['Post'].append(parse_post(item))

	to = None
	if data['pagingInfo']['next'] is not None:
		to = data['pagingInfo']['next']['to']
	return to, out


def paged_threaded_post_responses_query(cfg:str, url:str, to:int=None):
	
	url = urlparse(url)
	cfg = parse_curl(in_path=cfg)
	
	cfg['headers']['medium-frontend-path'] = url.path
	cfg['headers']['referer'] = url.geturl()
	cfg['data'][0]['variables']['postId'] = url.path.split('-')[-1]
	cfg['data'][0]['variables']['postResponsesPaging']['to'] = to
	cfg['data'][0]['query'] = cfg['data'][0]['query'].replace('\\n','\n') 

	_, _, data = rreq(
		cfg['url'],
		'post',
		ctype='json',
		cookies=cfg['cookies'],
		headers=cfg['headers'],
		json=cfg['data'],
		http2=True,
		max_retries=5,
		sleep=60
		)
	
	aid = data[0]['data']['post']['id']
	data = data[0]['data']['post']['threadedPostResponses']
	out = {'Comment' : [], 'Creator' : []}
	for item in data['posts']:
		out['Comment'].append(parse_comment(item, aid))
		out['Creator'].append(parse_creator(item['creator']))
	
	to = None
	if data['pagingInfo']['next'] is not None:
		to = data['pagingInfo']['next']['to']
	return to, out


def clap_mutation(cfg:str, url:str, target_id:str, num_claps:int=1) -> int:
	
	url = urlparse(url)
	cfg = parse_curl(in_path=cfg)
	
	cfg['headers']['medium-frontend-path'] = url.path
	cfg['headers']['referer'] = url.geturl()
	cfg['data'][0]['variables']['targetPostId'] = target_id
	cfg['data'][0]['variables']['numClaps'] = num_claps
	cfg['data'][0]['query'] = cfg['data'][0]['query'].replace('\\n','\n')

	_, _, data = rreq(
		cfg['url'],
		'post',
		ctype='json',
		cookies=cfg['cookies'],
		headers=cfg['headers'],
		json=cfg['data'],
		http2=True,
		max_retries=5,
		sleep=60
		)

	data = data[0]['data']['clap']
	return data['clapCount']


def user_profile_query(cfg:str, username:str, homepagePostsFrom:str=None):
	"""
	"""
	cfg = parse_curl(in_path=cfg)
	cfg['headers']['medium-frontend-path'] = f'/@{username}'
	cfg['headers']['referer'] = f'https://medium.com/@{username}'
	cfg['data'][0]['variables']['homepagePostsFrom'] = homepagePostsFrom
	cfg['data'][0]['variables']['username'] = username
	cfg['data'][0]['query'] = cfg['data'][0]['query'].replace('\\n','\n')
	
	_, _, data = rreq(
		cfg['url'],
		'post',
		ctype='json',
		cookies=cfg['cookies'],
		headers=cfg['headers'],
		json=cfg['data'],
		http2=True,
		max_retries=5,
		sleep=60
		)
	
	data = data[0]['data']['userResult']
	out = {'Collection' : [], 'Creator' : [], 'Tags' : [], 'Post' : []}
	data = data['homepagePostsConnection']
	for item in data['posts']:
		if item['collection'] is not None:
			out['Collection'].append(parse_collection(item['collection']))
		if item['pendingCollection'] is not None:
			out['Collection'].append(parse_collection(item['pendingCollection']))
		out['Creator'].append(parse_creator(item['creator']))
		out['Tags'].extend([
			(item['id'], t['displayTitle'], t['id'], t['normalizedTagSlug'])
			for t in item['tags']])
		out['Post'].append(parse_post(item))

	fr = None
	if data['pagingInfo']['next'] is not None:
		fr = data['pagingInfo']['next']['from']
	return fr, out
	
	