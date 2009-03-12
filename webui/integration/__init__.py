print "do Django server integration!"
from webui import settings
from rapidsms.config import Config
from django.conf.urls.defaults import *
import os
import sys
import string
import sets
#this is wrong, as we might actually have them already loaded
#right way is to do os.environ, get the ini and load up the definitive list of apps

ini = ""
conf = None
if "RAPIDSMS_INI" in os.environ:
    ini = os.environ["RAPIDSMS_INI"]
    conf = Config(ini)

templates_to_add = []
urls_to_add = []
for app_hash in conf["rapidsms"]["apps"]:
    app_name = app_hash['type']
    app_fullname = 'apps.' + app_name
    module = __import__(app_fullname, {}, {}, [''])
    templates_to_add.append(os.path.join(os.path.dirname(module.__file__),'templates'))
    try:
        urlmodule = module = __import__(app_fullname+".urls", {}, {}, [''])
        urls_to_add += patterns('',(r'^%s/' % (app_name), include(app_fullname + ".urls")))
    except:
        continue

settings.TEMPLATE_DIRS += templates_to_add

from webui import urls
urls.urlpatterns += urls_to_add

