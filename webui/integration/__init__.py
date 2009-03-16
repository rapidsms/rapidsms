print "do Django server integration!"
from webui import settings
from rapidsms.config import Config
from django.conf.urls.defaults import *
from django.templatetags import __path__
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
    templates_to_add.append(os.path.join(os.path.dirname(module.__file__),'webui/' + app_name + '/templates'))
    try:
        print app_fullname
        #urlmodule = __import__(app_fullname+".webui.urls", {}, {}, [''])
        urls_to_add += patterns('',(r'^%s/' % (app_name), include(app_fullname + ".webui.urls")))
        # try to extend django.templatetags.__path__ with app's templatetags
        __path__.extend(__import__(app_fullname + '.webui.' + app_name + '.templatetags', {}, {}, ['']).__path__)
    except Exception, e:
        print e

print 'templates_to_add: ' + str(templates_to_add)
settings.TEMPLATE_DIRS += templates_to_add

print 'templatetags.__path__'
print __path__

from webui import urls
print 'urls_to_add: ' + str(urls_to_add)
urls.urlpatterns += urls_to_add

