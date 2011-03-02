import sys
import re
import xml.dom.minidom
import config
import embedly
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
    

def oembed_replace(str=''):
     ns = str
     s = str
     oe = re.compile("\[http://(.*youtube\.com/watch.*|.*\.youtube\.com/v/.*|youtu\.be/.*|.*\.youtube\.com/user/.*#.*|.*\.youtube\.com/.*#.*/.*|.*justin\.tv/.*|.*justin\.tv/.*/b/.*|www\.ustream\.tv/recorded/.*|www\.ustream\.tv/channel/.*|qik\.com/video/.*|qik\.com/.*|.*revision3\.com/.*|.*\.dailymotion\.com/video/.*|.*\.dailymotion\.com/.*/video/.*|www\.collegehumor\.com/video:.*|.*twitvid\.com/.*|www\.break\.com/.*/.*|vids\.myspace\.com/index\.cfm\?fuseaction=vids\.individual&videoid.*|www\.myspace\.com/index\.cfm\?fuseaction=.*&videoid.*|www\.metacafe\.com/watch/.*|blip\.tv/file/.*|.*\.blip\.tv/file/.*|video\.google\.com/videoplay\?.*|.*revver\.com/video/.*|video\.yahoo\.com/watch/.*/.*|video\.yahoo\.com/network/.*|.*viddler\.com/explore/.*/videos/.*|liveleak\.com/view\?.*|www\.liveleak\.com/view\?.*|animoto\.com/play/.*|dotsub\.com/view/.*|www\.overstream\.net/view\.php\?oid=.*|www\.livestream\.com/.*|www\.worldstarhiphop\.com/videos/video.*\.php\?v=.*|worldstarhiphop\.com/videos/video.*\.php\?v=.*|teachertube\.com/viewVideo\.php.*|teachertube\.com/viewVideo\.php.*|bambuser\.com/v/.*|bambuser\.com/channel/.*|bambuser\.com/channel/.*/broadcast/.*|.*yfrog\..*/.*|tweetphoto\.com/.*|www\.flickr\.com/photos/.*|.*twitpic\.com/.*|.*imgur\.com/.*|.*\.posterous\.com/.*|post\.ly/.*|twitgoo\.com/.*|i.*\.photobucket\.com/albums/.*|gi.*\.photobucket\.com/groups/.*|phodroid\.com/.*/.*/.*|www\.mobypicture\.com/user/.*/view/.*|moby\.to/.*|xkcd\.com/.*|www\.xkcd\.com/.*|www\.asofterworld\.com/index\.php\?id=.*|www\.qwantz\.com/index\.php\?comic=.*|23hq\.com/.*/photo/.*|www\.23hq\.com/.*/photo/.*|.*dribbble\.com/shots/.*|drbl\.in/.*|.*\.smugmug\.com/.*|.*\.smugmug\.com/.*#.*|emberapp\.com/.*/images/.*|emberapp\.com/.*/images/.*/sizes/.*|emberapp\.com/.*/collections/.*/.*|emberapp\.com/.*/categories/.*/.*/.*|embr\.it/.*|picasaweb\.google\.com.*/.*/.*#.*|picasaweb\.google\.com.*/lh/photo/.*|picasaweb\.google\.com.*/.*/.*|dailybooth\.com/.*/.*|brizzly\.com/pic/.*|pics\.brizzly\.com/.*\.jpg|img\.ly/.*|www\.facebook\.com/photo\.php.*|www\.tinypic\.com/view\.php.*|tinypic\.com/view\.php.*|www\.tinypic\.com/player\.php.*|tinypic\.com/player\.php.*|www\.tinypic\.com/r/.*/.*|tinypic\.com/r/.*/.*|.*\.tinypic\.com/.*\.jpg|.*\.tinypic\.com/.*\.png|meadd\.com/.*/.*|meadd\.com/.*|.*\.deviantart\.com/art/.*|.*\.deviantart\.com/gallery/.*|.*\.deviantart\.com/#/.*|fav\.me/.*|.*\.deviantart\.com|.*\.deviantart\.com/gallery|.*\.deviantart\.com/.*/.*\.jpg|.*\.deviantart\.com/.*/.*\.gif|.*\.deviantart\.net/.*/.*\.jpg|.*\.deviantart\.net/.*/.*\.gif|www\.whitehouse\.gov/photos-and-video/video/.*|www\.whitehouse\.gov/video/.*|wh\.gov/photos-and-video/video/.*|wh\.gov/video/.*|www\.hulu\.com/watch.*|www\.hulu\.com/w/.*|hulu\.com/watch.*|hulu\.com/w/.*|movieclips\.com/watch/.*/.*/|movieclips\.com/watch/.*/.*/.*/.*|.*crackle\.com/c/.*|www\.fancast\.com/.*/videos|www\.funnyordie\.com/videos/.*|www\.vimeo\.com/groups/.*/videos/.*|www\.vimeo\.com/.*|vimeo\.com/groups/.*/videos/.*|vimeo\.com/.*|www\.ted\.com/talks/.*\.html.*|www\.ted\.com/talks/lang/.*/.*\.html.*|www\.ted\.com/index\.php/talks/.*\.html.*|www\.ted\.com/index\.php/talks/lang/.*/.*\.html.*|.*omnisio\.com/.*|.*nfb\.ca/film/.*|www\.thedailyshow\.com/watch/.*|www\.thedailyshow\.com/full-episodes/.*|www\.thedailyshow\.com/collection/.*/.*/.*|movies\.yahoo\.com/movie/.*/video/.*|movies\.yahoo\.com/movie/.*/info|movies\.yahoo\.com/movie/.*/trailer|www\.colbertnation\.com/the-colbert-report-collections/.*|www\.colbertnation\.com/full-episodes/.*|www\.colbertnation\.com/the-colbert-report-videos/.*|www\.comedycentral\.com/videos/index\.jhtml\?.*|www\.theonion\.com/video/.*|theonion\.com/video/.*|wordpress\.tv/.*/.*/.*/.*/|www\.traileraddict\.com/trailer/.*|www\.traileraddict\.com/clip/.*|www\.traileraddict\.com/poster/.*|www\.escapistmagazine\.com/videos/.*|www\.trailerspy\.com/trailer/.*/.*|www\.trailerspy\.com/trailer/.*|www\.trailerspy\.com/view_video\.php.*|www\.atom\.com/.*/.*/|fora\.tv/.*/.*/.*/.*|www\.spike\.com/video/.*|www\.gametrailers\.com/video/.*|gametrailers\.com/video/.*|www\.koldcast\.tv/video/.*|www\.koldcast\.tv/#video:.*|www\.godtube\.com/featured/video/.*|www\.tangle\.com/view_video.*|soundcloud\.com/.*|soundcloud\.com/.*/.*|soundcloud\.com/.*/sets/.*|soundcloud\.com/groups/.*|www\\.last\\.fm/music/.*|www\\.last\\.fm/music/+videos/.*|www\\.last\\.fm/music/+images/.*|www\\.last\\.fm/music/.*/_/.*|www\\.last\\.fm/music/.*/.*|www\.mixcloud\.com/.*/.*/|espn\.go\.com/video/clip.*|espn\.go\.com/.*/story.*|cnbc\.com/id/.*|cbsnews\.com/video/watch/.*|www\.cnn\.com/video/.*|edition\.cnn\.com/video/.*|money\.cnn\.com/video/.*|today\.msnbc\.msn\.com/id/.*/vp/.*|www\.msnbc\.msn\.com/id/.*/vp/.*|www\.msnbc\.msn\.com/id/.*/ns/.*|today\.msnbc\.msn\.com/id/.*/ns/.*|multimedia\.foxsports\.com/m/video/.*/.*|msn\.foxsports\.com/video.*|.*amazon\..*/gp/product/.*|.*amazon\..*/.*/dp/.*|.*amazon\..*/dp/.*|.*amazon\..*/o/ASIN/.*|.*amazon\..*/gp/offer-listing/.*|.*amazon\..*/.*/ASIN/.*|.*amazon\..*/gp/product/images/.*|www\.amzn\.com/.*|amzn\.com/.*|www\.shopstyle\.com/browse.*|www\.shopstyle\.com/action/apiVisitRetailer.*|www\.shopstyle\.com/action/viewLook.*|gist\.github\.com/.*|twitter\.com/.*/status/.*|twitter\.com/.*/statuses/.*|www\.slideshare\.net/.*/.*|.*\.scribd\.com/doc/.*|screenr\.com/.*|polldaddy\.com/community/poll/.*|polldaddy\.com/poll/.*|answers\.polldaddy\.com/poll/.*|www\.5min\.com/Video/.*|www\.howcast\.com/videos/.*|www\.screencast\.com/.*/media/.*|screencast\.com/.*/media/.*|www\.screencast\.com/t/.*|screencast\.com/t/.*|issuu\.com/.*/docs/.*|www\.kickstarter\.com/projects/.*/.*|www\.scrapblog\.com/viewer/viewer\.aspx.*|my\.opera\.com/.*/albums/show\.dml\?id=.*|my\.opera\.com/.*/albums/showpic\.dml\?album=.*&picture=.*|tumblr\.com/.*|.*\.tumblr\.com/post/.*|www\.polleverywhere\.com/polls/.*|www\.polleverywhere\.com/multiple_choice_polls/.*|www\.polleverywhere\.com/free_text_polls/.*|.*\.status\.net/notice/.*|identi\.ca/notice/.*|shitmydadsays\.com/notice/.*)]", re.I)
     urls = oe.findall(s)
     oembed_json = embedly.get_multi(urls,maxwidth=480)

     for idx,item in enumerate(oembed_json):
         try:
             title = item['title']
         except KeyError:
             title = ''
         try:
             url = item['url']
         except KeyError:
             url = ''
         try:
             thumbnail_url = item['thumbnail_url']
         except KeyError:
             thumbnail_url = ''
         r = ''
         if item['type'] == 'photo': 
            r = ' <a href="http://' + urls[idx] + '" target="_blank"><img src="' + url + '" alt="' + title + '"/></a>'
         if item['type'] == 'video':
            r = ' '+item['html']
         if item['type'] == 'rich':
            r = ' '+item['html']
         if item['type'] == 'link':
            r = ' <a href="' + url + '">' + title + '</a>'
         #s = re.sub('\[http://'+urls[idx]+']', r, s)
     return r