import os

import views as pv

from django.conf.urls.defaults import *

urlpatterns = patterns('',

	# serve assets via django, during development
	(r'^poll/assets/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/assets"}),
	
	# graphs are generated and stored to be viewed statically
    (r'^poll/graphs/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/graphs"}),

	# poll views (move to poll/urls.py)
	(r'^poll$', pv.dashboard),
	(r'^poll/dashboard$', pv.dashboard),
	(r'^poll/dashboard/(?P<id>\d+)$', pv.dashboard),
	(r'^poll/questions$', pv.manage_questions),
	(r'^poll/question/(?P<id>\d+)$', pv.manage_questions),
	(r'^poll/question/(?P<id>\d+)/edit$', pv.edit_question),
	(r'^poll/question/add$', pv.add_question),
	(r'^poll/log$', pv.message_log),
	
	# ajax
	(r'^poll/moderate/(?P<id>\d+)/(?P<status>win|fail)$', pv.moderate),
	(r'^poll/correct/(?P<id>\d+)$', pv.correction),\

)
