import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__),'apps'))
sys.path.append(os.path.join(os.path.dirname(__file__),'lib'))


os.environ['RAPIDSMS_INI'] = os.path.join(os.path.dirname(__file__),'rapidsms.ini')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapidsms.djangoproject.settings'
from rapidsms.djangoproject import settings

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
