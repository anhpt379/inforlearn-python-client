"""
How API Works?

  - get consumer key/secret
  - get access_token
  - login
  - post/comment/get_messages/get_info
"""

from simplejson import loads, dumps
import urllib2
import oauth
#from settings import *

JSON_URL = 'http://localhost:8080/api/json'
NS_DOMAIN = 'inforlearn.com'


class API:
  def __init__(self, consumer_key,
                     consumer_secret,
                     access_token_key, 
                     access_token_secret):
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token_key = access_token_key
    self.access_token_secret = access_token_secret
    
  def _request(self, parameters):
    consumer = oauth.OAuthConsumer(self.consumer_key, self.consumer_secret)
    access_token = oauth.OAuthToken(self.access_token_key, self.access_token_secret)
    request = oauth.OAuthRequest.from_consumer_and_token(oauth_consumer=consumer,
                                                         token=access_token,
                                                         http_url=JSON_URL,
                                                         http_method='POST',
                                                         parameters=parameters)
    request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
                         consumer,
                         access_token)
    result = urllib2.urlopen(urllib2.Request(JSON_URL,
                                             request.to_postdata()))
    data = result.read()
    result.close()
    return loads(data)
    
  def connect(self, actor_nick):
    parameters = {"nick": actor_nick + '@' + NS_DOMAIN,
                  "method": "get_info"}
    result = self._request(parameters)
    if result['status'] == 'success':
      if result['response']['actor']['type'] == 'user':
        return User(result, 
                    self.consumer_key, 
                    self.consumer_secret,
                    self.access_token_key, 
                    self.access_token_secret)
      if result['response']['actor']['type'] == 'channel':
        return Channel(result, 
                       self.consumer_key, 
                       self.consumer_secret,
                       self.access_token_key, 
                       self.access_token_secret)
      
  def get_messages(self, actor_nick, limit=20, offset="2010-10-25 14:30:59"):
    parameters = {"nick": actor_nick + '@' + NS_DOMAIN,
                  "limit": limit,
                  "offset": offset,
                  "method": "get_messages"}
    output = []
    result = self._request(parameters)
    print dumps(result, indent=2)
    if result['status'] == 'success':
      entries = result['response']['entries']
      for entry in entries:
        if entry['entry'] is None:
          output.append(Message(entry), 
                        self.consumer_key, 
                        self.consumer_secret,
                        self.access_token_key, 
                        self.access_token_secret)
        else:
          output.append(Comment(entry))
    return output


class Channel(API):  
  def __init__(self, info_dict,
                     consumer_key,
                     consumer_secret,
                     access_token_key, 
                     access_token_secret):
    self.info = info_dict['response']['actor']
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token_key = access_token_key
    self.access_token_secret = access_token_secret
  
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
  
  def post(self, message, location, nick):
    nick = nick + '@' + NS_DOMAIN
    params = {'message': message,
              'location': location,
              'nick': nick,
              'icon': 0,
              'method': 'post'}
    result = self._request(params)
    return result

  
class User(API):
  def __init__(self, info_dict,
                     consumer_key,
                     consumer_secret,
                     access_token_key, 
                     access_token_secret):
    self.info = info_dict['response']['actor']
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token_key = access_token_key
    self.access_token_secret = access_token_secret
  
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
  
  def post(self, message, location):
    nick = self.nick + '@' + NS_DOMAIN
    params = {'message': message,
              'location': location,
              'nick': nick,
              'icon': 0,
              'method': 'post'}
    result = self._request(params)
    return result
    

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
  def __init__(self, entry_dict, 
                     consumer_key,
                     consumer_secret,
                     access_token_key, 
                     access_token_secret):
    self.entry = entry_dict
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token_key = access_token_key
    self.access_token_secret = access_token_secret
  
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
  
  def add_comment(self, content, nick): 
    stream = "stream/%s/comments" % (self.actor)
    entry = "stream/%s/presence/%s" % (self.owner, self.uuid)
    nick = nick + '@' + NS_DOMAIN
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
  api = API("b3c5e9952f9f4fa2994278964d7694b0",
            "bf56567651504f22a2d86e952e3759b0",
            "f79836d985064bbf9d375c217b6fcd49", 
            "63963c7f0fb148ac94fb78c99f5478ca")
#  print api.get_info("AloneRoad").full_name
#  print api.get_info("AloneRoad").avatar
#  print dumps(api.get_messages("AloneRoad"), indent=2)
#  print api.get_info("#status").rank
#  entries = api.get_messages("AloneRoad")
##  for entry in entries:
##    print entry.type
#  first_message = entries[0]
#  print first_message.add_comment("test comment via api", 'AloneRoad')
  user = api.connect("Admin")
  print user.full_name
  channel = api.connect("#inforlearn")
  print channel.raw_format()
  print channel.external_url
  print channel.post("post to channel via api", "HN", "AloneRoad")
#  print ar.post("message via api", "Hanoi")
  