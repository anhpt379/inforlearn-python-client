#!/usr/bin/python 
import oauth, httplib
import urllib2

#Define Constants 
KEY = '0299cc35f5ca45cf9f1974f056fea080' #Change Me 
SECRET = '181a73a06ea04d9f964c020e518a531a' #Change Me 
SERVER = 'www.jaiku.com' 
REQURL = '/api/request_token' 
REQUEST_TOKEN_URL = '/api/request_token'
ACCESS_TOKEN_URL = 'http://www.jaiku.com/access_token'
AUTHORIZATION_URL = 'http://www.jaiku.com/authorize'

if __name__ == "__main__":  
  consumer = oauth.OAuthConsumer(KEY, SECRET)
  access_token = oauth.OAuthToken('88480d7c8e7248b9b1a674217df5762a', '5f9cab3c72e342b9a71a681a7b45a897')
  parameters = {'nick': 'AloneRoad', 'method': 'actor_get'}
  request = oauth.OAuthRequest.from_consumer_and_token(oauth_consumer=consumer,
                                                       token=access_token,
                                                       http_url='http://api.jaiku.com/json',
                                                       http_method='POST',
                                                       parameters=parameters)
  request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
                       consumer,
                       access_token)
  result = urllib2.urlopen(urllib2.Request('http://api.jaiku.com/json',
                                           request.to_postdata()))
  print result.read()
  result.close()