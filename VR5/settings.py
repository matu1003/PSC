from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [dict(name='session2', num_demo_participants=None, app_sequence=['VR5']), dict(name='listebasique', num_demo_participants=None, app_sequence=['liste_aveugle_basique_3']), dict(name='my_session', num_demo_participants=None, app_sequence=['listef_connue_basique']), dict(name='VR_test', num_demo_participants=None, app_sequence=['VR3']), dict(name='vr_5', num_demo_participants=None, app_sequence=['VR5'])]
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = []
SESSION_FIELDS = []
ROOMS = [dict(name='my_room', display_name='my_room')]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']


