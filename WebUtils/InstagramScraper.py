from WebUtils.utils import rget


class InstagramScraper:
	"""
	
	Simple instagram scraper to collect data.
	
	WARNING:
		use with caution. You may risk getting banned from the platform.
	
	"""
	
	
	def __init__(self, cookies:dict, headers:dict) -> None:
		"""
		
		Args:
			cookies_path : dictionary with cookies indexed by account.
			headers_path : dictionary with headers indexed by account.

		"""
		
		self.headers = headers
		self.cookies = cookies

	
	def user_info(self, username:str, account:str) -> dict:
		"""
		
		Collects user info.
		Does not require authentication.
		
		Args:
			username : username of the profile.
			account : account to use to gather the info
		
		Returns:
			profile information
		
		"""
		
		return rget(
				'https://i.instagram.com/api/v1/users/web_profile_info/',
				headers=self.headers[account],
				cookies=self.cookies[account],
				params={'username': username},
				ctype='json',
				sleep=1,
				cumul=True
			)
	
	
	def followers(self, userid:str, account:str, 
			   max_id:str=None, count:str='12') -> dict:
		"""
		
		Collect {count} followers of {userid} starting from {max_id}.
		Requires authentication.
		
		Args:
			userid : userid of the profile
			account : account to use to gather the info
			max_id (optional) : starting position
			count (optional) : number of followers to retrieve
		
		Returns:
			followers information
		
		"""
		
		params = {
				'max_id' : max_id,
				'count': count,
				'search_surface': 'follow_list_page'
			}
		
		if params['max_id'] in [None,'0']:
			del params['max_id']		

		return rget(
				f'https://i.instagram.com/api/v1/friendships/{userid}/followers/',
				headers=self.headers[account],
				cookies=self.cookies[account],
				params=params,
				ctype='json',
				sleep=1,
				cumul=True
			)
		 