from WebUtils.ThreadedTwitter import ThreadedTwitter

tt = ThreadedTwitter('config/WebUtils/twitterapi_cred.yaml')

tt.put(get_friend_ids=('twitter',-1,1))
print(tt.get('get_friend_ids'))
print('\n')

tt.put(get_friends=('twitter',-1,1))
print(tt.get('get_friends'))
print('\n')

tt.put(get_follower_ids=('twitter',-1,1))
print(tt.get('get_follower_ids'))
print('\n')

tt.put(get_followers=('twitter',-1,1))
print(tt.get('get_followers'))
print('\n')

del tt
