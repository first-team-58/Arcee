import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'RiotCrew.settings'
sys.path.append('/srv/django')
sys.path.append('/srv/django/RiotCrew')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
