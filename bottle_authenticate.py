import bottle
import inspect
import time
import urllib

_URL_LOGIN_FORM = '/login'
_URL_LOGIN = '/login'
_URL_LOGOUT = '/logout'
_DEST_DEFAULT = '/'
_TPL_FORM_DEFAULT = 'login/login.tpl'
_KEYWORD_DEFAULT = 'authname'
_BASEURL_DEFAULT = ''
_TIMEOUT_DEFAULT = 3600
_COOKIENAME_DEFAULT = 'bottleauthenticate'
_COOKIEPATH = '/'

class BottleAuthenticatePlugin(object):
  ''' Login wrapper for bottle route methods'''

  name = 'authenticate'
  api = 2

  def __init__(self,\
          cb_authenticate,\
          secret,\
          baseurl=_BASEURL_DEFAULT,\
          tpl_form=_TPL_FORM_DEFAULT,\
          dest_default=_DEST_DEFAULT,\
          timeout=_TIMEOUT_DEFAULT,\
          cookie_name=_COOKIENAME_DEFAULT,
          keyword=_KEYWORD_DEFAULT):
    self.secretKey=secret
    self.timeout = timeout
    self.keyword = keyword
    self.cookie_name = cookie_name
    self.baseurl = baseurl.rstrip('/')
    self.authenticate =  cb_authenticate
    self.tpl_form = tpl_form
    self.dest_default = dest_default

  def setup(self, app):
    ''' Make sure that other installed plugins don't affect the same
        keyword argument.'''
    for other in app.plugins:
      if not isinstance(other, BottleAuthenticatePlugin): continue
      if other.keyword == self.keyword:
        raise PluginError("Found another plugin with "\
        "conflicting settings (non-unique keyword).")

    app.route(_URL_LOGIN_FORM, 'GET',  self.login_form)
    app.route(_URL_LOGIN, 'POST', self.do_login)
    app.route(_URL_LOGOUT, 'GET', self.do_logout)

  def apply(self, callback, route):
    # Test if the original callback accepts the keyword.
    args = inspect.getargspec(route.callback)[0]
    if self.keyword not in args:
      return callback

    def wrapper(*args, **kwargs):
      cookie=self.check_cookie()

      if cookie:
        kwargs[self.keyword] = cookie['username']
        rv = callback(*args, **kwargs)
      else:
        arg = { 'dest' : bottle.request.url }
        encarg = urllib.parse.urlencode(arg)
        bottle.redirect(self.baseurl + _URL_LOGIN_FORM + '?' + encarg)

      return rv

    # Replace the route callback with the wrapped one.
    return wrapper


  def check_cookie(self):
    cookie = bottle.request.get_cookie(self.cookie_name, secret=self.secretKey)

    # cookie must not be empty 
    # cookies must not be copied to a different machine
    # cookies must not be too old 
    if not cookie \
    or cookie.get('ip',None) != bottle.request.environ.get('REMOTE_ADDR')\
    or (time.time() - cookie.get('timestamp',0)) > self.timeout:
        bottle.response.delete_cookie( self.cookie_name, path=_COOKIEPATH )
        return None

    return cookie

  def login_form(self):
    cookie = self.check_cookie()
    dest = bottle.request.query.get('dest', self.dest_default)
    if not cookie:
        return bottle.template(self.tpl_form, \
                { 'actionurl' : self.baseurl + _URL_LOGIN, \
                  'destination' : dest }) 
    else:
      bottle.redirect(dest)

  def do_login(self):
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')
    dest = bottle.request.forms.get('destination', self.dest_default)

    if self.authenticate(username, password):
      self.set_cookie(username)

      bottle.redirect(dest)
    else:
      return bottle.template(self.tpl_form, \
              { 'destination': dest, \
                'actionurl' : self.baseurl + _URL_LOGIN, \
                'status' : 'failed'})

  def set_cookie(self, username):
    content = { 'username'  :username,\
                'ip'        : bottle.request.environ\
                .get('REMOTE_ADDR'),\
                'timestamp' : time.time()
              }
    bottle.response.set_cookie(self.cookie_name, content, path=_COOKIEPATH,\
                               max_age=self.timeout, secret=self.secretKey)
  

  def do_logout(self):
    bottle.response.delete_cookie(self.cookie_name, path=_COOKIEPATH)
    dest = bottle.request.query.get('dest', self.dest_default)

    bottle.redirect(dest)
