import os
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

config = {}

config['site'] = {
    'name': 'Pagify',
    'url': 'http://pagifyapp.appspot.com',
    'description': 'Create custom Facebook pages',
    'google_analytics_id': '',
}

if not debug:
    config['facebook'] = {
        'app_id': '141947329155355',
        'app_secret': '3e48982a6ea78c23afce0209e96fcc7a',
        'api_key': 'a284fdd504b5191923362afabc0ea6c7',
    }

if debug:
    config['facebook'] = {
        'app_id': '186997311337233',
        'app_secret': 'edf36480fd0b7b1e40af15dda796ec81',
        'api_key': '0874652ff3b6b35cf768ea03b3063ad1',
    }

config['google'] = {
    'api_key': 'AIzaSyBWk2VmSTr0NZEcYvE7o11A7Rkl4gRF-LY',
    'jquery_version': '1.4.4',
    'jquery_ui_version': '1.8.9',
}

config['spreedly'] = {
    'api_version': '4',
    'api_key': 'fe6f8493ee741d99708072645be6de0e5e06f0c9',
    'site_name': 'pagify-test',
    'plans': {"plus-1":"8023","plus-2":"8024","plus-3":"8025","plus-4":"8026","plus-5":"8027"}
}

config['extras.sessions'] = {
    'secret_key': 'eu9hym7ru6i5fos3ghan2uc7nid9tul3ik7pec7in3foc8waph',
}