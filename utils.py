import sys
import xml.dom.minidom
import config
import webapp2 as webapp
from pprint import pprint
from Crypto.Cipher import ARC4 as cipher


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
    enc = cipher.new(config.config['extras.sessions']['secret_key'])
    x = enc.encrypt(str)
    return x
  
def decrypt(str):
    dec = cipher.new(config.config['extras.sessions']['secret_key'])
    y = dec.decrypt(str)
    return y
  