from django.urls import include, path
from django.contrib import admin

from rapidsms import views as rapidsms_views

admin.autodiscover()

urlpatterns = (
    path('admin/', admin.site.urls),

    # RapidSMS core URLs
    path('account/', include('rapidsms.urls.login_logout')),
    path('', rapidsms_views.dashboard, name='rapidsms-dashboard'),

    # RapidSMS contrib app URLs
    path('httptester/', include('rapidsms.contrib.httptester.urls')),
    path('messagelog/', include('rapidsms.contrib.messagelog.urls')),
    path('messaging/', include('rapidsms.contrib.messaging.urls')),
    path('registration/', include('rapidsms.contrib.registration.urls')),

    # Third party URLs
    path('selectable/', include('selectable.urls')),
)
