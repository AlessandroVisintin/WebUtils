from WebUtils.utils import get, parse_curl


# get online JSON
#URL = 'https://jsonplaceholder.typicode.com/todos/1'
#print(get(URL, ctype='json'), '\n')

# extract headers from cURL command
PATH = 'config/WebUtils/medium_SearchQuery.curl'
print(parse_curl(in_path=PATH))
