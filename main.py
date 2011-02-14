import os
import sys
import config
if 'lib' not in sys.path:
    # Add /lib as primary libraries directory
    sys.path[0:0] = ['lib']

# Import Webapp2
import webapp2 as webapp
from webapp2 import RedirectHandler, Route
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

# Error Handlers    
class Handle404(webapp.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        template_values = {
            'config': self.get_config('site'),
            }
            
        self.response.set_status(404)
        path = os.path.join(os.path.dirname(__file__), "templates/errors", '404.html')
        self.response.out.write(template.render(path, template_values))

class Handle500(webapp.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        template_values = {
            'config': self.get_config('site'),
            }

        self.response.set_status(500)
        path = os.path.join(os.path.dirname(__file__), "templates/errors", '500.html')
        self.response.out.write(template.render(path, template_values))

# Is this the development server?
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

app = webapp.WSGIApplication([
    #Front-End Routes
    Route('/<page:(|privacy|terms)>', 'handlers.PageHandler', name='frontend-pages'),
    #App Routes
    Route('/dashboard', 'handlers.DashboardHandler', name='dashboard'),
    Route('/edit/page/<pageid:\d+>', 'handlers.EditPageHandler', name='edit-page'),
    Route('/settings', 'handlers.SettingsHandler', name='settings'),
    Route('/upgrade', 'handlers.UpgradeHandler', name='upgrade'),
    Route('/upload', 'handlers.UploadHandler', name='upload'),
    Route('/api/<method:(scripturl|headerimageurl|getwidget|savewidget|savepageorder|deletewidget|saveoption)>', 'handlers.AjaxApiHandler', name='api'),
    Route('/listen', 'handlers.ListenHandler', name='api'),
    #Facebook Routes
    Route('/canvas/', 'handlers.fbCanvasHandler', name='fb-canvas'),
    Route('/canvas/tab/', 'handlers.fbTabHandler', name='fb-tab')
    ],config=config.config,debug=debug)

# Error Handlers
app.error_handlers[404] = Handle404
#if not debug:
#    app.error_handlers[500] = Handle500

# Instantiate the application
def main():
    app.run()


if __name__ == '__main__':
    main()
