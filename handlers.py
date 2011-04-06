import os
import sys
if 'lib' not in sys.path:
    # Add /lib as primary libraries directory
    sys.path[0:0] = ['lib']
import datetime
import facebook
import logging
import re
import urllib
import spreedly
import base64
import hashlib
#import markdown
import webapp2 as webapp
from xml.dom import minidom
from utils import fblogin_required,encrypt,decrypt, xmltodict,oembed_replace
from models import User, Page, UploadedFiles, Widget, Option
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext import deferred
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.api import capabilities
from django.utils import simplejson
#from django.contrib.markup.templatetags import markup 

# Session Extention
#import extras.extension_support
#import extras.sessions  

#deferred functions

def get_subscriber_changes(id):
    try:
        response = spreedly.request('subscribers/%s.xml' % id, 'get')
        if response:  
            #dom = minidom.parseString(response)
            #customer_id = dom.getElementsByTagName('customer-id')[0].firstChild.data
            user = User.get_by_key_name(id)
            user.subscriber_info = response
            user.put()
    except:
        logging.error(id)
        
def get_embedly_code(args):
    id = args["id"]
    url = args["url"]
    type = args["type"]
    logging.info(args)
    try:
        response = oembed_replace(url)
        if response:  
            widget = Widget.get_by_key_name(id)
            if type == "embedly":
                widget.embedly_code = db.Text(response)
            if type == "googlemaps":
                widget.googlemaps_code = db.Text(response)
            widget.put()
    except:
        logging.error(id)
        logging.error(url)
        
        
#base Handler
class BaseHandler(webapp.RequestHandler):
    #plugins = [extras.sessions.SessionPlugin()]
    #@property
    #def sessions(self):
    #    return self.request.registry.get('extras.sessions.SessionStore')
    # Load a session. # Set a session value. session['foo'] = 'bar'
    #session = self.sessions.get_session()
    # Get flash messages. self.sessions.set_flash('some value')
    #flashes = self.sessions.get_flash()
    @property
    def current_user(self):
        try:
            """Returns the active user, or None if the user has not logged in."""
            if not hasattr(self, "_current_user"):
                self._current_user = None
                cookie = facebook.get_user_from_cookie(
                    self.request.cookies, self.get_config('facebook', 'app_id'), self.get_config('facebook', 'app_secret'))
                if cookie:
                    # Store a local instance of the user data so we don't need
                    # a round-trip to Facebook on every request
                    user = User.get_by_key_name(cookie["uid"])
                    if not user:
                        graph = facebook.GraphAPI(cookie["access_token"])
                        profile = graph.get_object("me")
                        user = User(key_name=str(profile["id"]),
                                    id=str(profile["id"]),
                                    name=profile["name"],
                                    email=profile["email"],
                                    profile_url=profile["link"],
                                    access_token=cookie["access_token"])
                        user.put()
                    elif user.access_token != cookie["access_token"]:
                        user.access_token = cookie["access_token"]
                        user.put()
                    self._current_user = user
            return self._current_user
        except:
            self._current_user = None

    @property
    def graph(self):
        """Returns a Graph API client for the current user."""
        if not hasattr(self, "_graph"):
            if self.current_user:
                self._graph = facebook.GraphAPI(self.current_user.access_token)
            else:
                self._graph = facebook.GraphAPI()
        return self._graph

    def render(self, path, **kwargs):
        args = dict(config=self.get_config('site'),
                    current_user=self.current_user,
                    facebook=self.get_config('facebook'),
                    google=self.get_config('google')
                    )
        args.update(kwargs)
        try:
          if self.current_user.subscriber_info:
              args.update(dict(subscriber_info=simplejson.loads(self.current_user.subscriber_info)))
        except:
          pass
        path = os.path.join(os.path.dirname(__file__), "templates", path)
        datastore_write_enabled = capabilities.CapabilitySet('datastore_v3', capabilities=['write']).is_enabled()
        if datastore_write_enabled and path != "app/fb-tab.html":
            self.response.out.write(template.render(path, args))
        else:
            self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), "templates","app", "maintenance.html"), args))
    
class PageHandler(BaseHandler):
    def get(self, **kwargs):
        pages = ['app/login']
        page = kwargs.get('page')
        if page is '':
            page = 'app/login'
        if self.current_user and (page in pages):
            self.redirect('/dashboard')
        else:
            self.render(page+".html", )
         
class DashboardHandler(BaseHandler):
    @fblogin_required
    def get(self, **kwargs):
        ''' See if coming from payment'''
        if self.request.get("s") == '1':
            get_subscriber_changes(self.current_user.id)
            
        '''Get Users Pages From Facebook'''
        try:
            fb_users_pages = self.graph.get_connections("me", "accounts")
            fb_page_ids = []
            for p in fb_users_pages['data']:
                if p['category'] != 'Application' or p['id'] == '141947329155355':
                  fb_page_ids.append(p["id"])
            fb_pages = self.graph.get_objects(fb_page_ids)
            
            '''Update Pages Cache'''
            batch = []
            for k,fb_page in fb_pages.items():
                try:
                    picture = fb_page["picture"]
                except KeyError:
                    picture = None
                try:
                    fan_count = fb_page["fan_count"]
                except KeyError:
                    fan_count = None
                try:
                    has_added_app = fb_page["has_added_app"]
                except KeyError:
                    has_added_app = None
                try:
                    category = fb_page["category"]
                except KeyError:
                    category = None
                page = Page.get_by_key_name(fb_page["id"])
                if not page:
                    page = Page(key_name=str(fb_page["id"]),
                                id=str(fb_page["id"]),
                                name=fb_page["name"],
                                link=fb_page["link"],
                                category=category,
                                picture=picture,
                                fan_count=str(fan_count),
                                has_added_app=has_added_app
                                )
                    batch.append(page)
                else:
                    page.picture = picture
                    page.fan_count=str(fan_count)
                    page.has_added_app = has_added_app
                    batch.append(page)
            if batch:                 
                page_keys = db.put(batch)
                user = self.current_user
                user.pages = page_keys
                db.put(user)
                             
        except facebook.GraphAPIError:
            pass
            
        """Get Users Pages"""
        try:
            user = self.current_user
            pages = Page.get(user.pages)
            self.render("app/dashboard.html", admin=True,pages=pages)    
        except:
            pass    
         
class EditPageHandler(BaseHandler):
    @fblogin_required
    def get(self, **kwargs): 
        admin = False 
        user =  self.current_user  
        page_id = kwargs.get('pageid')
        options_dict = {}
        try:
            pages = Page.get(user.pages)
            for p in pages:
                if p.id == page_id:
                    admin = True
                    page = p
                    widgets = Widget.all().filter('page =', page).filter('deleted = ', False).order('order')
                    options = Option.all().filter('type_reference =', page)
                    for option in options:
                        options_dict[option.name] = {'id': str(option.key().id()), 'value': option.value}
                    
        except:
            page = None
            widgets = None
            options_dict = None
        if admin:
            #page = Page.get_by_key_name(str(page_id))
            #add_app_url = 'https://www.facebook.com/add.php?api_key=a284fdd504b5191923362afabc0ea6c7&pages=1&page=141947329155355'
            upload_url = blobstore.create_upload_url('/upload')
            page_id = encrypt(page_id).encode('hex')
            self.render("app/edit.html", admin=True, page=page,upload_url=upload_url, page_id=page_id,widgets= widgets, options=options_dict) 
        else:
            self.redirect('/dashboard')
            
class SettingsHandler(BaseHandler):
    @fblogin_required
    def get(self, **kwargs):  
        try:
            dom = minidom.parseString(self.current_user.subscriber_info)
            token = dom.getElementsByTagName('token')[0].firstChild.data  
            change_suscription_url = 'https://spreedly.com/%s/subscriber_accounts/%s' % (self.get_config('spreedly','site_name'),token)
        except:
            change_suscription_url = None
        self.render("settings.html", admin=True,change_suscription_url=change_suscription_url)
                
class UpgradeHandler(BaseHandler):
    @fblogin_required
    def get(self, **kwargs):  
        user =  self.current_user
        name =  user.name.split()
        fname = name[0]
        lname = name[len(name)-1]
        pages = Page.get(user.pages)
        page_id = self.request.get("p")
        self.render("app/upgrade.html", admin=True, pages=pages, page_id=page_id, user=user, fname=fname, lname=lname)
        
class AjaxApiHandler(BaseHandler):
    @fblogin_required
    def get(self, **kwargs):
        user =  self.current_user
        admin = False
        method = kwargs.get('method')
        if method == 'scripturl':
            upload_url = blobstore.create_upload_url('/upload')
            
            self.response.out.write(upload_url)
        if method == 'headerimageurl':
            #pages = Page.get(user.pages)
            key_name = self.request.get("p")
            #for p in pages:
            #    if p.id == page_id:
            #        page = p
            #        admin = True
            #if admin:
            page = Page.get_by_key_name(key_name)
            if page:
                header_image_url = page.header_image_url
                
                self.response.out.write(header_image_url)
            else:
                
                self.response.out.write('')
        if method == 'getwidget':
            widget_id = self.request.get("wid")
            widget = Widget.get_by_key_name(widget_id)
            tenr = range(1,11)
            if widget:
                widget_type = widget.type
            if not widget:
                widget_type = self.request.get("wtype").lstrip('wi-')
                widget = dict(type=widget_type,
                            id=widget_id
                            )
            if widget_type:
                self.render('app/widgets/'+widget_type+".html", widget=widget,tenr=tenr)
            else:
                
                self.response.out.write("This widget cannot be found.")
    def post(self, **kwargs):
        user =  self.current_user
        admin = False
        method = kwargs.get('method')
        if method == 'deletewidget':
            key_name = self.request.get("wid")
            widget = Widget.get_by_key_name(key_name)
            if widget:
                widget.deleted = True
                widget.last_modified_by = user
            try:
                db.put(widget)
                self.response.out.write('True')
            except:
                self.response.out.write('False')
                
        if method == 'savepageorder':
            page_order = self.request.get('pageorder')
            page_order = page_order.split(',')
            batch = []
            for k,v in enumerate(page_order):
                widget = Widget.get_by_key_name(v)
                if widget:
                    widget.order = k
                    widget.last_modified_by = user
                    batch.append(widget)
            try:
                db.put(batch)
                self.response.out.write('True')
            except:
                self.response.out.write('False')
                
        if method == 'savewidget':
            page = Page.get_by_key_name(self.request.get('pageid'))
            key_name = self.request.get('wid')
            widget = Widget.get_by_key_name(key_name)
            if self.request.get('wtype') == 'embedly':
               fields = simplejson.loads(self.request.get('wcontents'))
               #get_embedly_code({'id':self.request.get('wid'),"url":fields['embedly_url'],"type":"embedly"})
               deferred.defer(get_embedly_code,{'id':self.request.get('wid'),"url":fields['embedly_url'],"type":"embedly"})
            if self.request.get('wtype') == 'googlemaps':
               fields = simplejson.loads(self.request.get('wcontents'))
               deferred.defer(get_embedly_code,{'id':self.request.get('wid'),"url":fields['googlemaps_link'],"type":"googlemaps"})
            if not widget:
                widget = Widget(key_name=key_name,
                                id = key_name,
                                type = self.request.get('wtype'),
                                name = self.request.get('wname'),
                                page = page,
                                contents = self.request.get('wcontents'),
                                last_modified_by = user
                               )
                fields = simplejson.loads(self.request.get('wcontents'))
                for k,v in fields.iteritems():
                    db_type = k.split('__')
                    try:
                        db_type = db_type[1]
                    except IndexError:
                        db_type = None
                    logging.info(db_type)
                    if db_type == 'text':
                        setattr(widget, k, db.Text(v))
                    else:
                        setattr(widget, k, v)
            else:
                widget.name = self.request.get('wname')
                widget.contents = self.request.get('wcontents')
                widget.last_modified_by = user
                fields = simplejson.loads(self.request.get('wcontents'))
                for k,v in fields.iteritems():
                    db_type = k.split('__')
                    try:
                        db_type = db_type[1]
                    except IndexError:
                        db_type = None
                    logging.info(db_type)
                    if db_type == 'text':
                        setattr(widget, k, db.Text(v))
                    else:
                        setattr(widget, k, v)
            
            try:
                db.put(widget)
                self.response.out.write('True')
            except:
                self.response.out.write('False')
        if method == 'saveoption':
            try:
                option = Option.get_by_id(int(self.request.get('id')))
            except:
                option = None
            if self.request.get('otype') == 'page':
                link = Page.get_by_key_name(self.request.get('opageid'))
            if not option:
                option = Option(
                                name = self.request.get('oname'),
                                value = self.request.get('ovalue'),
                                type = self.request.get('otype'),
                                type_reference = link
                               )
            else:
                option.value = self.request.get('ovalue')
                
            try:
                db.put(option)
                self.response.out.write('True')
            except:
                self.response.out.write('False')
        if method == 'upgradedowngrade':
          try:
            username = self.get_config('saasy','username')
            password = self.get_config('saasy','password')
            product = self.get_config('saasy','product')
            qty = str(self.request.get('qty'))
            basic_auth = base64.b64encode('%s:%s' % (username, password)) 
            xml_data = "<subscription><productPath>/%s</productPath><quantity>%s</quantity><no-end-date/></subscription>" % (product,qty)
            subscriber_info=simplejson.loads(self.current_user.subscriber_info)
            url = "https://api.fastspring.com/company/seedprod/subscription/%s" % subscriber_info['reference']
            response = urlfetch.fetch(url=url,payload=xml_data,headers={'Authorization': 'Basic %s' % basic_auth ,'Content-Type': 'application/xml' },method=urlfetch.PUT)
            if response.status_code == 200:
              # Update Pages
              upgraded_pages = self.request.get('pages').split(',')
              pages = Page.get(user.pages)
              batch = []
              for p in pages:
                if p.id in upgraded_pages:
                  p.upgraded = '1'
                  p.upgraded_by = user
                else:
                  if p.upgraded_by:
                    if p.upgraded_by.id == user.id:
                      p.upgraded = '0'
                      p.upgraded_by = None
                batch.append(p)
              db.put(batch)
                           
              self.response.out.write('True')
            else:
              self.response.out.write('False')
          except:
            self.response.out.write('False')
               
               
''' Listen for changes from subscribers'''
class ListenHandler(webapp.RequestHandler):  
    def post(self, **kwargs):
        #try:
            privatekey = '792ec9274bc52418e995f355e3a8a4d1'
            if hashlib.md5(self.request.get("security_data") + privatekey).hexdigest() != self.request.get("security_hash"):
                self.abort(500)
            referrer = urllib.unquote(self.request.get("referrer"))
            referrer = referrer.split('|')
            uid = referrer[0]
            pages = referrer[1]
    
            subscriber_info = {}
            subscriber_info['details'] = self.request.get("details")
            subscriber_info['event'] = self.request.get("event")
            subscriber_info['productname'] = self.request.get("productname")
            subscriber_info['quantity'] = self.request.get("quantity")
            subscriber_info['reference'] = self.request.get("reference")
            subscriber_info['uid'] = uid
            subscriber_info['pages'] = pages
            subscriber_info['status'] = self.request.get("status")
            subscriber_info['type'] = self.request.get("type")
            subscriber_info['enddate'] = self.request.get("enddate")
            subscriber_info['nextperioddate'] = self.request.get("nextperioddate")
            subscriber_info = simplejson.dumps(subscriber_info)
            user = User.get_by_key_name(uid)
            user.subscriber_info = subscriber_info
            db.put(user)
            if self.request.get("event") == 'Active':
                pages = pages.split(',');
                batch = []
                for p in pages:
                    page = Page.get_by_key_name(p)
                    if page:
                        page.upgraded = '1'
                        page.upgraded_by = user
                        batch.append(page)
                db.put(batch)
            if self.request.get("event") == 'Inactive':
                pages = Page.all().filter('upgraded_by =', user)
                batch = []
                for p in pages:
                        p.upgraded = '0'
                        p.upgraded_by = None
                        batch.append(p)
                db.put(batch)
                
            self.response.set_status(500)
        #except:
        #    logging.error('Listen Error')
        #    self.abort(500)
        
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, **kwargs):
        batch = []
        blob_info = self.get_uploads('Filedata')[0]
        page_id = re.sub('\/edit\/page\/','',self.request.get('folder'))
        page_id = re.sub('\D*','', decrypt(page_id.decode('hex')))
        header_image_url = images.get_serving_url(str(blob_info.key()))
        
        #update uploaded file info
        uploaded_file = UploadedFiles.get_by_key_name(page_id)
        if not uploaded_file:
            uploaded_file = UploadedFiles(key_name=page_id,blob=blob_info.key(),page_id=page_id)
            batch.append(uploaded_file) 
        else:
            blobstore.delete(uploaded_file.blob.key())
            uploaded_file.blob=blob_info.key()
            batch.append(uploaded_file)
        
        #update page info
        page = Page.get_by_key_name(page_id)
        page.header_image_url = header_image_url
        batch.append(page) 
        
        if batch:
            db.put(batch)
        self.response.set_status(302)
        
''' Facebook FrontEnd '''  
class fbCanvasHandler(BaseHandler):
    '''def get(self, **kwargs):
        self.render("app/fb-canvas.html", )
    def post(self, **kwargs):
        self.render("app/fb-canvas.html", )'''
    def get(self, **kwargs):
        page_id = self.request.get('page_id')
        try:
            page = Page.get_by_key_name(page_id)
            widgets = Widget.all().filter('page =', page).filter('deleted = ', False).order('order')
        except:
            page=None
            widgets=None
        self.render("app/fb-tab.html", page=page,widgets=widgets, method="get")

class fbTabHandler(BaseHandler):
    def post(self, **kwargs):
        #logging.info(self.request)
        signed_request = facebook.parse_signed_request(self.request.get('signed_request'),self.get_config('facebook','app_secret'))
        #logging.info(signed_request)
        try:
          user_id = signed_request['user_id']
        except:
          user_id = None
        page_id = signed_request['page']['id']
        liked = signed_request['page']['liked']
        admin = signed_request['page']['admin']
        options_dict = {}
        status = 'True'
        try:
          page = Page.get_by_key_name(page_id)
          #check active account or for expired account.
          if page.upgraded != '1':

            expire_date = page.created + datetime.timedelta(days=30)
            min_expire_date = datetime.datetime(2011,7,1)
        
            if (expire_date < min_expire_date):
              expire_date = min_expire_date

            if expire_date < datetime.datetime.now():
              status = 'False'

          
          
          widgets = Widget.all().filter('page =', page).filter('deleted = ', False).order('order')
          options = Option.all().filter('type_reference =', page)
          for option in options:
              options_dict[option.name] = {'id': str(option.key().id()), 'value': option.value}
        except:
          page=None
          widgets=None
          options_dict = None
        self.render("app/fb-tab.html", page=page,widgets=widgets, method="post",options=options_dict,admin=admin,status=status)



        