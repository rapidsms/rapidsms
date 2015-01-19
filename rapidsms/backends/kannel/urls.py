from django.conf.urls import include, url
from rapidsms.backends.kannel import views


urlpatterns = (
    url(r'^account/', include('rapidsms.urls.login_logout')),
    url(r"^delivery-report/$",
        views.DeliveryReportView.as_view(),
        name="kannel-delivery-report"),
    url(r"^backend/kannel/$",
        views.KannelBackendView.as_view(backend_name='kannel-backend'),
        name='kannel-backend'),
)
