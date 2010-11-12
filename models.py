from google.appengine.ext import db
from google.appengine.ext import blobstore

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    email = db.StringProperty()
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    pages = db.ListProperty(db.Key)
    subscriber_info = db.TextProperty()
    options = db.TextProperty()
    
class Page(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    link = db.StringProperty(required=True)
    category = db.StringProperty()
    picture = db.StringProperty()
    fan_count = db.StringProperty()
    has_added_app = db.BooleanProperty()
    plan = db.StringProperty(choices=('free','plus'), default='free')
    header_image_url = db.StringProperty()
    
class UploadedFiles(db.Model):
    blob = blobstore.BlobReferenceProperty(required=True)
    page_id = db.StringProperty(required=True) 
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    
#class UserPage(db.Model): 
#    user = db.ReferenceProperty(User) 
#    page = db.ReferenceProperty(Page)

class Widget(db.Expando):
    id = db.StringProperty(required=True)
    type = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    order = db.IntegerProperty(default=0)
    page = db.ReferenceProperty(Page,collection_name='widgets')
    last_modified_by = db.ReferenceProperty(User)
    deleted = db.BooleanProperty(default=False)

    
class Option(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    value = db.StringProperty(required=True)
    type = db.ReferenceProperty()
