import os
import sys
import datetime
import facebook
import logging
import re
import urllib
import spreedly
import base64
import webapp2 as webapp
from xml.dom import minidom
from utils import fblogin_required,encrypt,decrypt, xmltodict
from models import User, Page, UploadedFiles, Widget, Option
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext import deferred
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from django.utils import simplejson

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
        path = os.path.join(os.path.dirname(__file__), "templates", path)
        self.response.out.write(template.render(path, args))
    
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
        try:
            pages = Page.get(user.pages)
            for p in pages:
                if p.id == page_id:
                    page = p
                    widgets = Widget.all().filter('page =', page).filter('deleted = ', False).order('order')
                    admin = True
        except:
            page = None
            widgets = None
        if admin:
            #page = Page.get_by_key_name(str(page_id))
            add_app_url = 'https://www.facebook.com/add.php?api_key=a284fdd504b5191923362afabc0ea6c7&pages=1&page=141947329155355'
            upload_url = blobstore.create_upload_url('/upload')
            page_id = encrypt(page_id).encode('hex')
            self.render("app/edit.html", admin=True, page=page,upload_url=upload_url, page_id=page_id,widgets= widgets) 
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
        pages = Page.get(user.pages)
        page_id = self.request.get("p")
        plans = self.get_config('spreedly','plans')
        try:
            dom = minidom.parseString(self.current_user.subscriber_info)
            token = dom.getElementsByTagName('token')[0].firstChild.data
            subscribe_url = 'https://spreedly.com/%s/subscribers/%s/%s/subscribe/%s' % (self.get_config('spreedly','site_name'),user.id,token,'${plan_id}')
        except:
            subscribe_url = 'https://spreedly.com/%s/subscribers/%s/subscribe/%s/%s' % (self.get_config('spreedly','site_name'),user.id,'${plan_id}',urllib.quote(user.name))
        
        return_url = '?return_url=' + urllib.quote(self.get_config('site','url') + '/dashboard' + '?s=1&p=') + '${page_ids}'
        subscribe_url = subscribe_url + return_url
        
        
        self.render("upgrade.html", admin=True, subscribe_url=subscribe_url,pages=pages, page_id=page_id, plans=plans)
        
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
            if widget:
                widget_type = widget.type
            if not widget:
                widget_type = self.request.get("wtype").lstrip('wi-')
                widget = dict(type=widget_type,
                            id=widget_id
                            )
            if widget_type:
                self.render('app/widgets/'+widget_type+".html", widget=widget)
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
                    setattr(widget, k, v)
            else:
                widget.name = self.request.get('wname')
                widget.contents = self.request.get('wcontents')
                widget.last_modified_by = user
                fields = simplejson.loads(self.request.get('wcontents'))
                for k,v in fields.iteritems():
                    setattr(widget, k, v)
            
            try:
                db.put(widget)
                self.response.out.write('True')
            except:
                self.response.out.write('False')
            
                
''' Listen for changes from Spreedly'''
class ListenHandler(webapp.RequestHandler):  
    def post(self, **kwargs):
        try:
            subscriber_ids = self.request.get("subscriber_ids").split(',')
            for i in subscriber_ids:
                deferred.defer(get_subscriber_changes, i)
            self.response.set_status(200)
        except:
            logging.error('Listen Error: ' + self.request.get("subscriber_ids"))
            self.abort(500)
        
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
    def get(self, **kwargs):
        self.render("app/fb-canvas.html", )
    def post(self, **kwargs):
        self.render("app/fb-canvas.html", )

class fbTabHandler(BaseHandler):
    def get(self, **kwargs):
        self.render("app/fb-tab.html", post=self.request.get('fb_sig_page_id'),method='get')
    def post(self, **kwargs):
        page_id = self.request.get('fb_sig_page_id')
        try:
            page = Page.get_by_key_name(page_id)
            widgets = Widget.all().filter('page =', page).filter('deleted = ', False).order('order')
        except:
            widgets=None
        self.render("app/fb-tab.html", page=page,widgets=widgets)
         
class WallHandler(BaseHandler):
    #@fblogin_required
    def get(self, **kwargs):
        try:
            news_feed = self.graph.get_connections("me", "feed")
        except facebook.GraphAPIError:
            self.render("index.html", config=self.get_config('site'))
            return
        except:
            news_feed = {"data": []}
        for post in news_feed["data"]:
            post["created_time"] = datetime.datetime.strptime(
                post["created_time"], "%Y-%m-%dT%H:%M:%S+0000") + \
                datetime.timedelta(hours=7)
        self.render("wall.html", news_feed=news_feed)
        
               
class PostHandler(BaseHandler):
    def post(self):
        message = self.request.get("message")
        if not self.current_user or not message:
            self.redirect("/")
            return
        try:
            self.graph.put_wall_post(message)
        except:
            pass
        self.redirect("/")


        