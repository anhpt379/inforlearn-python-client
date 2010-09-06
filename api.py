"""
>>> api = API(KEY, SECRET)
>>> api.connect("AloneRoad")
>>> api.get_info()
>>> api.send_message("content", "your location")
>>> stream = api.get_stream()
>>> stream[1].add_comment('content')

"""

from simplejson import loads, dumps
import urllib2
import urlparse
import oauth
import oauth2
from time import sleep


REQUEST_TOKEN_URL = 'http://localhost:8080/api/request_token'
ACCESS_TOKEN_URL = 'http://localhost:8080/api/access_token'
AUTHORIZE_URL = 'http://localhost:8080/api/authorize'

JSON_URL = 'http://localhost:8080/api/json'
NS_DOMAIN = 'inforlearn.com'


class API:
  def __init__(self, your_consumer_key, your_consumer_secret):
    global consumer_key
    global consumer_secret
    consumer_key = your_consumer_key
    consumer_secret = your_consumer_secret
    
  def come_back(self, username, last_access_token_key, last_access_token_secret):
    global access_token_key
    global access_token_secret
    global user
    user = username
    access_token_key = last_access_token_key
    access_token_secret = last_access_token_secret    
      
  def connect(self, actor_nick, perms="delete"):
    """ permission: read/write/delete """
    request_token_url = REQUEST_TOKEN_URL
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    
    global user
    user = actor_nick    
    
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)
    
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])
    
    request_token = dict(urlparse.parse_qsl(content))
       
    print "Open the following link in your browser:"
    print "%s?oauth_token=%s&perms=%s" % (authorize_url, request_token['oauth_token'], perms)
    print 
    
    sleep(2)  # wait user copy url and open it in browser
    access_token = ''
    while True:
      try:
        token = oauth2.Token(request_token['oauth_token'],
            request_token['oauth_token_secret'])
        token.set_verifier('')
        client = oauth2.Client(consumer, token)
        
        resp, content = client.request(access_token_url, "POST")
        html = urlparse.parse_qsl(content)
        access_token = dict(html)
        access_token['oauth_token']
        break
      except KeyError:
        sleep(1)
        continue
        
      
    print "OK. Have fun ^^"
      
    global access_token_key
    global access_token_secret
    access_token_key = access_token['oauth_token']
    access_token_secret = access_token['oauth_token_secret']
    return [access_token_key, access_token_secret]     
    
  def _request(self, params):
    consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
    access_token = oauth.OAuthToken(access_token_key, access_token_secret)
    request = oauth.OAuthRequest.from_consumer_and_token(oauth_consumer=consumer,
                                                         token=access_token,
                                                         http_url=JSON_URL,
                                                         http_method='POST',
                                                         parameters=params)
    request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
                         consumer,
                         access_token)
    result = urllib2.urlopen(urllib2.Request(JSON_URL,
                                             request.to_postdata()))
    data = result.read()
    result.close()
    return loads(data)
  
  def get_info(self):
    params = {"nick": user + '@' + NS_DOMAIN,
              "method": "get_info"}
    result = self._request(params)
    if result['status'] == 'success':
      if result['response']['actor']['type'] == 'user':
        return User(result)
      if result['response']['actor']['type'] == 'channel':
        return Channel(result)
  
  def send_message(self, message, location):
    nick = user + '@' + NS_DOMAIN
    params = {'message': message,
              'location': location,
              'nick': nick,
              'icon': 0,
              'method': 'send_message'}
    result = self._request(params)
    return result
      
  def get_stream(self, limit=20, offset="2010-10-25 14:30:59"):
    parameters = {"nick": user + '@' + NS_DOMAIN,
                  "limit": limit,
                  "offset": offset,
                  "method": "get_stream"}
    output = []
    result = self._request(parameters)
    print dumps(result, indent=2)
    if result['status'] == 'success':
      entries = result['response']['entries']
      for entry in entries:
        if entry['entry'] is None:
          output.append(Message(entry))
        else:
          output.append(Comment(entry))
    return output
  
    
class Channel(API):  
  def __init__(self, info_dict):
    self.info = info_dict['response']['actor']
  
  @property
  def nick(self):
    return self.info["nick"].split("@")[0]
  
  @property
  def privacy(self):
    if self.info['privacy'] == 3:
      return "public"
    return "private"
  
  @property
  def type(self):
    return self.info['type']
  
  @property
  def rank(self):
    return self.info['rank']
    
  @property
  def member_count(self):
    return self.info['extra']['follower_count']
  
  @property
  def description(self):
    return self.info['extra']['description']
  
  @property
  def external_url(self):
    if self.info['extra'].has_key('external_url'):
      return self.info['extra']['external_url']
    return None
      
  @property
  def avatar(self):
    return '/image/' + self.info['extra']['icon'] + '_f.jpg'
    
  def raw_format(self):
    return dumps(self.info, indent=2)

  
class User(API):
  def __init__(self, info_dict):
    self.info = info_dict['response']['actor']
  
  @property
  def nick(self):
    return self.info["nick"].split("@")[0]
  
  @property
  def privacy(self):
    if self.info['privacy'] == 3:
      return "public"
    return "private"
  
  @property
  def type(self):
    return self.info['type']
  
  @property
  def rank(self):
    return self.info['rank']
  
  @property
  def homepage(self):
    return self.info['extra']['homepage']
  
  @property
  def follower_count(self):
    return self.info['extra']['follower_count']
  
  @property
  def contact_count(self):
    return self.info['extra']['contact_count']
  
  @property
  def full_name(self):
    return self.info['extra']['full_name']
  
  @property
  def avatar(self):
    return '/image/' + self.info['extra']['icon'] + '_f.jpg'
    
  def raw_format(self):
    return dumps(self.info, indent=2)


class Comment:
  def __init__(self, entry_dict):
    self.entry = entry_dict
    
  @property
  def uuid(self):
    return self.entry['uuid']
  
  @property
  def content(self):
    return self.entry['extra']['content']
  
  @property
  def message(self):
    return self.entry['extra']['entry_title']
  
  @property
  def message_owner(self):
    return self.entry['extra']['entry_actor']
  
  @property
  def message_uuid(self):
    return self.entry['extra']['entry_uuid']
    
  @property
  def created_at(self):
    return self.entry['created_at']
  
  @property
  def actor(self):
    return self.entry['actor']
  
  @property
  def owner(self):
    return self.entry['owner']
  
  @property
  def type(self):
    return 'comment'
  

class Message(API):
  def __init__(self, entry_dict):
    self.entry = entry_dict
  
  @property
  def uuid(self):
    return self.entry['uuid']
  
  @property
  def content(self):
    return self.entry['extra']['title']
  
  @property
  def location(self):
    return self.entry['extra']['location']
  
  @property
  def created_at(self):
    return self.entry['created_at']
  
  @property
  def actor(self):
    return self.entry['actor']
  
  @property
  def owner(self):
    return self.entry['owner']
  
  @property
  def type(self):
    return 'message'
  
  def add_comment(self, content): 
    stream = "stream/%s/comments" % (self.actor)
    entry = "stream/%s/presence/%s" % (self.owner, self.uuid)
    nick = user + '@' + NS_DOMAIN
    params = {'stream': stream,
              'entry': entry,
              'content': content,
              'nick': nick,
              'method': 'add_comment'}
    result = self._request(params)
    return result
      
  def raw_format(self):
    return dumps(self.entry, indent=2)


if __name__ == "__main__":
  CONSUMER_KEY = 'b3c5e9952f9f4fa2994278964d7694b0'
  CONSUMER_SECRET = 'bf56567651504f22a2d86e952e3759b0'
  api = API(CONSUMER_KEY, CONSUMER_SECRET)
  from os import path
  if not path.exists("access_token.secret"):
    access_token = api.connect("AloneRoad", "delete")
    if access_token:
      open("access_token.secret", "w").write(str(access_token))
  else:
    access_token = open("access_token.secret").read()
    access_token = eval(access_token)
    api.come_back("AloneRoad", access_token[0], access_token[1])
  print api.get_info().full_name
  print api.send_message("test", "test")
  for i in api.get_stream():
    print i.content
