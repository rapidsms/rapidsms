from django.conf.urls.defaults import *

from rapidsms.backends.kannel import views


urlpatterns = patterns('',
    url(r"^backend/kannel/$",
        views.KannelBackendView.as_view(backend_name='kannel-backend'),
        name='kannel-backend'),
)
