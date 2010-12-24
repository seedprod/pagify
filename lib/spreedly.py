import sys
import base64
import config
import logging
from google.appengine.api import urlfetch

def request(request=None, method='get'):
  if method == 'get':
      method=urlfetch.GET
  elif method == 'post':
      method=urlfetch.POST
  username = config.config['spreedly']['api_key']
  password = 'X'
  response = None
  url = "https://spreedly.com/api/v%s/%s/%s" % (config.config['spreedly']['api_version'],config.config['spreedly']['site_name'],request)
  basic_auth = base64.b64encode('%s:%s' % (username, password)) 
  if request:
    response = urlfetch.fetch(url=url,headers={'Authorization': 'Basic %s' % basic_auth },method=urlfetch.GET)
  if response.status_code == 200:
    response = response.content
    return response
  else:
    return None
    