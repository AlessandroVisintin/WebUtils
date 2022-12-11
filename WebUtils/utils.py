import curlparser
from bs4 import BeautifulSoup
from httpx import Client, ReadTimeout

import json
from typing import Any

from JSONWrap.utils import dump
from WebUtils.StoppableSleep import StoppableSleep


def get(url:str, **kwargs) -> tuple[bool,int,Any]:
	"""
	Get online resource. Supports http2 request.
		
	Args:
		url : resource address
		**kwargs :
			ctype (str) : expected content type. Supports 'json', 'html'.
				Defaults to plain text
			cookies (dict) : cookies to append to the request.
			headers (dict) : headers to append to the request.
			params (dict) : parameters to append to the request.
			http2 (bool) : enable HTTP2 request. Default to False.

	Returns:
		tuple : (
			parsed (bool), (status code,headers), parsed data)
			The parsed datatype depends on the provided ctype.
			JSON -> JSON object
			HTML -> BeatifulSoup object
	"""
	try:
		headers = kwargs['headers']
	except KeyError:
		headers = None
	try:
		cookies = kwargs['cookies']
	except KeyError:
		cookies = None
	try:
		params = kwargs['params']
	except KeyError:
		params = None
	try:
		http2 = kwargs['http2']
	except KeyError:
		http2 = False

	try:
		with Client(http2=http2, headers=headers, cookies=cookies) as c:
			r = c.get(url, params=params)
	except ReadTimeout:
		return False, (408,None), None

	state = (r.status_code, r.headers.raw)
	try:
		if kwargs['ctype'] == 'json':
			try:
				return True, state, json.loads(r.text)
			except json.JSONDecodeError:
				return False, state, {}
		elif kwargs['ctype'] == 'html':
			return True, state, BeautifulSoup(r.text, 'lxml')
		else:
			return True, state, r.text
	except KeyError:
		return True, state, r.text


def post(url:str, **kwargs) -> tuple[bool,int,Any]:
	"""
	Post to online server. Supports http2 request.
		
	Args:
		url : resource address
		**kwargs :
			ctype (str) : expected content type. Supports 'json', 'html'.
				Defaults to plain text
			cookies (dict) : cookies to append to the request.
			headers (dict) : headers to append to the request.
			json (dict) : data to append to the request.
			http2 (bool) : enable HTTP2 request. Default to False.

	Returns:
		tuple : (
			parsed (bool), (status code,headers), parsed data)
			The parsed datatype depends on the provided ctype.
			JSON -> JSON object
			HTML -> BeatifulSoup object	
	"""
	try:
		headers = kwargs['headers']
	except KeyError:
		headers = None
	try:
		cookies = kwargs['cookies']
	except KeyError:
		cookies = None
	try:
		data = kwargs['json']
	except KeyError:
		data = None
	try:
		http2 = kwargs['http2']
	except KeyError:
		http2 = False

	try:
		with Client(http2=http2, headers=headers, cookies=cookies) as c:
			r = c.post(url, json=data)
	except ReadTimeout:
		return False, (408,None), None

	state = (r.status_code, r.headers.raw)
	try:
		if kwargs['ctype'] == 'json':
			try:
				return True, state, json.loads(r.text)
			except json.JSONDecodeError:
				return False, state, {}
		elif kwargs['ctype'] == 'html':
			return True, state, BeautifulSoup(r.text, 'lxml')
		else:
			return True, state, r.text
	except KeyError:
		return True, state, r.text


def rget(url:str, **kwargs) -> Any:
	"""
		
	Retry request until successfully performed.
	Defaults to infinite retries.
		
	Args:
		url : see get() method
		**kwargs :
			verbose (bool) : print error if True. Defaults to False.
			max_retries (int) : max number of retries
			sleep (int) : delay between two consecutive tries
			cumul (bool) : sleep time doubles at each cycle. 
			See get() method for additional kwargs.
		
	Returns:
		Parsed data.

	Raises:
		RuntimeError: max retries reached.

	"""
	
	clock = StoppableSleep()
	try:
		verbose = kwargs['verbose']
	except KeyError:
		verbose = False
		
	while True:
		parsed, state, data = get(url, **kwargs)				
		if parsed and state[0] == 200:
			return state[1], data
		
		if verbose: print(state, data)
		
		try:
			if kwargs['max_retries'] > 0:
				kwargs['max_retries'] -= 1
			else:
				raise RuntimeError
		except KeyError:
			pass
		
		try:
			if kwargs['sleep'] > 0:
				clock.sleep(kwargs['sleep'])
				if kwargs['cumul']:
					kwargs['sleep'] += kwargs['sleep']
		except KeyError:
			pass 


def parse_curl(**kwargs) -> dict:
	"""
	Parse cURL headers.
	cURL command can be passed either as string or file.
	The ouput can be optionally stored.
	Supports both JSON and YAML.
	
	Args:
		**kwargs
			curl : string with curl command
			in_path : path/to/curl_file
			out_path : path/to/storage
	
	Returns:
		parsed curl command.
		{'headers' : dict(headers) [, cookies : dict(cookies)]}
	"""
	curl = ''
	if 'curl' in kwargs:
		curl = kwargs['curl']
	elif 'in_path' in kwargs:
		with open(kwargs['in_path'], 'r') as f:
			curl = f.read()
	curl = curl.replace('--compressed', '')
	res = curlparser.parse(curl)
	
	out = {
		'url' : res.url,
		'method' : res.method,
		'headers' : {
			str(k).lower() : str(v).strip() for k,v in res.header.items()},
		'cookies' : {},
		'data' : None
		}

	if 'cookie' in out['headers']:
		for c in out['headers']['cookie'].split(';'):
			k,v = c.split('=', 1)
			out['cookies'][k.strip()] = v.strip()
		del out['headers']['cookie']
	
	if res.data is not None:
		d = res.data[1:] if res.data.startswith('$') else res.data
		out['data'] = json.loads(d)

	try:
		dump(out, kwargs['out_path'])
	except KeyError:
		pass

	return out
