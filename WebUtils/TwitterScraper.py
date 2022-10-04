from json import dumps
from WebUtils.utils import rget


class TwitterScraper:
	"""
	
	Simple Twitter scraper to collect data.
	
	WARNING:
		use with caution. You may get banned from the platform.
	
	"""
	
	
	def __init__(self, cookies:dict, headers:dict, endpoints:dict) -> None:
		"""
		
		Args:
			cookies : dictionary with cookies indexed by account.
			headers : dictionary with headers indexed by account.
			endpoints : dictionary with API endpoints.

		"""
		
		self.headers = headers
		self.cookies = cookies
		self.endpoints = endpoints


	def user_info(self, username:str, account:str):
		"""
		
		Collects user info.
		Does not require authentication.
		
		Args:
			username : username of the profile.
			account : account to use to gather the info
		
		Returns:
			profile information
		
		"""
		
		headers = dict(self.headers[account])
		headers['referer'] = f'https://twitter.com/{username}'
		
		variables = {
				"screen_name":username,
				"withSafetyModeUserFields":True,
				"withSuperFollowsUserFields":True
			}

		features = {
				"responsive_web_graphql_timeline_navigation_enabled":False,
				"unified_cards_ad_metadata_container_dynamic_card_content_query_enabled":True,
				"responsive_web_uc_gql_enabled":True,
				"vibe_api_enabled":True,
				"responsive_web_edit_tweet_api_enabled":True,
				"graphql_is_translatable_rweb_tweet_is_translatable_enabled":False,
				"standardized_nudges_misinfo":True,
				"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,
				"interactive_text_enabled":True,
				"responsive_web_text_conversations_enabled":False,
				"responsive_web_enhance_cards_enabled":True
			}
		
		params = {
				'variables' : dumps(variables),
				'features' : dumps(features)
			}
		
		endpoint = self.endpoints[account]['user_info']
		
		return rget(
				f'https://twitter.com/i/api/graphql/{endpoint}/UserByScreenName',
				headers=headers,
				cookies=self.cookies[account],
				params=params,
				ctype='json',
				sleep=1,
				http2=True,
				cumul=True,
				verbose=True
			)


	def followers(self, username:str, userid:str, account:str,
			   cursor:str='-1', count:int=20):
		"""
		
		Collect {count} followers of {userid} starting from {cursor}.
		Requires authentication.
		
		Args:
			username : username of the profile
			userid : userid of the profile
			account : account to use to gather the info
			cursor (optional) : starting position
			count (optional) : number of followers to retrieve (max 100)
		
		Returns:
			followers information
		
		"""
		
		headers = dict(self.headers[account])
		headers['referer'] = f'https://twitter.com/{username}/followers'
		
		variables = {
				"userId":userid,
				"count":count,
				"cursor":str(cursor),
				"includePromotedContent":False,
				"withSuperFollowsUserFields":True,
				"withDownvotePerspective":True,
				"withReactionsMetadata":False,
				"withReactionsPerspective":False,
				"withSuperFollowsTweetFields":True
			}
		
		features = {
				"responsive_web_graphql_timeline_navigation_enabled":False,
				"unified_cards_ad_metadata_container_dynamic_card_content_query_enabled":True,
				"responsive_web_uc_gql_enabled":True,
				"vibe_api_enabled":True,
				"responsive_web_edit_tweet_api_enabled":True,
				"graphql_is_translatable_rweb_tweet_is_translatable_enabled":False,
				"standardized_nudges_misinfo":True,
				"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,
				"interactive_text_enabled":True,
				"responsive_web_text_conversations_enabled":False,
				"responsive_web_enhance_cards_enabled":True
			}
		
		params = {
				'variables' : dumps(variables),
				'features' : dumps(features)
			}

		endpoint = self.endpoints[account]['followers']
		return rget(
				f'https://twitter.com/i/api/graphql/{endpoint}/Followers',
				headers=headers,
				cookies=self.cookies[account],
				params=params,
				ctype='json',
				sleep=1,
				http2=True,
				cumul=True,
				verbose=True
			)
 