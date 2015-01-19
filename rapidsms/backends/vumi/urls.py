from django.conf.urls import include, url
from rapidsms.backends.vumi import views


urlpatterns = (
    url(r'^account/', include('rapidsms.urls.login_logout')),
    url(r"^backend/vumi/$",
        views.VumiBackendView.as_view(backend_name='vumi-backend'),
        name='vumi-backend'),
)
