from django.conf.urls.defaults import *

from rapidsms.backends.vumi import views


urlpatterns = patterns('',
    url(r"^(?P<backend_name>[\w-]+)/$", views.VumiBackendView.as_view(),
        name='vumi-backend'),
)
