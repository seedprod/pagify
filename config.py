import os
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

config = {}

config['site'] = {
    'name': 'Pagify',
    'url': 'http://pagifyapp.appspot.com',
    'description': 'Create Custom Facebook Pages',
    'google_analytics_id': 'UA-499993-13',
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
config['mailchimp'] = {
    'apikey': '41bd6a767d1f213b4e7dc87c88e11493-us2',
}    
config['saasy'] = {
    'username': 'api',
    'password': 'ckemendent',
    'product': 'pagifypro',
}
config['google'] = {
    'api_key': 'AIzaSyBWk2VmSTr0NZEcYvE7o11A7Rkl4gRF-LY',
    'jquery_version': '1.4.4',
    'jquery_ui_version': '1.8.9',
}

config['extras.sessions'] = {
    'secret_key': 'eu9hym7ru6i5fos3ghan2uc7nid9tul3ik7pec7in3foc8waph',
}