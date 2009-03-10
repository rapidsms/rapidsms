import os

import poll.views as pv

# magic admin stuff (remove during prod)
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	# serve assets via django, during development
	(r'^assets/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/assets"}),
	
	# graphs are generated and stored to be viewed statically
    (r'^graphs/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/graphs"}),

	# poll views (move to poll/urls.py)
	(r'^$', pv.dashboard),
	(r'^question/(?P<id>\d+)$', pv.dashboard),
	(r'^add$', pv.add_question),
	(r'^log$', pv.message_log),
	
	# ajax
	(r'^moderate/(?P<id>\d+)/(?P<status>win|fail)$', pv.moderate),
	(r'^correct/(?P<id>\d+)$', pv.correction),\

    # enable the django magic admin
    (r'^admin/(.*)', admin.site.root),
)
