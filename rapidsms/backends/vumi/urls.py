from django.urls import include, path
from rapidsms.backends.vumi import views


urlpatterns = (
    path('account/', include('rapidsms.urls.login_logout')),
    path('backend/vumi/',
        views.VumiBackendView.as_view(backend_name='vumi-backend'),
        name='vumi-backend'),
)
