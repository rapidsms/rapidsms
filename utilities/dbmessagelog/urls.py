from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import httplog.views as views

admin.autodiscover()

urlpatterns = patterns('',
    # allow the admin to hijack things first, 
    # but after that everything gets routed to
    # the API 
    (r'^admin/(.*)', admin.site.root),
    (r'^(.*)', views.api),
    
)
