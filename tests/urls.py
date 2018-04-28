from django.conf.urls import include, url
from django.contrib import admin

from rapidsms import views as rapidsms_views

admin.autodiscover()

urlpatterns = (
    url(r'^admin/', admin.site.urls),

    # RapidSMS core URLs
    url(r'^account/', include('rapidsms.urls.login_logout')),
    url(r'^$', rapidsms_views.dashboard, name='rapidsms-dashboard'),

    # RapidSMS contrib app URLs
    url(r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    url(r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    url(r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    url(r'^registration/', include('rapidsms.contrib.registration.urls')),

    # Third party URLs
    url(r'^selectable/', include('selectable.urls')),
)
