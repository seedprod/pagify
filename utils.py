import sys
import re
import xml.dom.minidom
import config
from embedly import Embedly
import logging
import webapp2 as webapp

# XML to Dict
def xmltodict(xmlstring):
	doc = xml.dom.minidom.parseString(xmlstring)
	remove_whilespace_nodes(doc.documentElement)
	return elementtodict(doc.documentElement)

def elementtodict(parent):
	child = parent.firstChild
	if (not child):
		return None
	elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
		return child.nodeValue

	d={}
	while child is not None:
		if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
			try:
				d[child.tagName]
			except KeyError:
				d[child.tagName]=[]
			d[child.tagName].append(elementtodict(child))
		child = child.nextSibling
	return d

def remove_whilespace_nodes(node, unlink=True):
	remove_list = []
	for child in node.childNodes:
		if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
			remove_list.append(child)
		elif child.hasChildNodes():
			remove_whilespace_nodes(child, unlink)
	for node in remove_list:
		node.parentNode.removeChild(node)
		if unlink:
			node.unlink()
			
# login decorator
def fblogin_required(func):
    def decorated(self, *args, **kwargs):
        return _login_required(self) or func(self, *args, **kwargs)
    return decorated
def _login_required(handler):
    if not handler.current_user:
        handler.redirect('/')
    return 
    
def encrypt(str):
    x = str.encode('base64').encode('hex')
    return x
  
def decrypt(str):
    y = str.decode('hex').decode('base64')
    return y
    
def oembed_replace(srcurl=''):
     r = ''
     client = Embedly()
     obj = client.oembed(srcurl,maxwidth=480)
     #for idx,item in enumerate(oembed_json):
     try:
         title = obj['title']
     except KeyError:
         title = ''
     try:
         url = obj['url']
     except KeyError:
         url = ''
     try:
         thumbnail_url = obj['thumbnail_url']
     except KeyError:
         thumbnail_url = ''
     
     if obj['type'] == 'photo': 
        r = ' <a href="http://' + srcurl + '" target="_blank"><img style="width:480px" src="' + url + '" alt="' + title + '"/></a>'
     if obj['type'] == 'video':
        r = ' '+obj['html']
     if obj['type'] == 'rich':
        r = ' '+obj['html']
     if obj['type'] == 'link':
        r = ' <a href="' + url + '">' + title + '</a>'

     return r