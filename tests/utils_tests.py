from WebUtils.utils import get, parse_curl_headers


# get online JSON
URL = 'https://jsonplaceholder.typicode.com/todos/1'
print(get(URL, ctype='json'), '\n')

# extract headers from cURL command
PATH = 'config/WebUtils/example.curl'
print(parse_curl_headers(in_path=PATH))
