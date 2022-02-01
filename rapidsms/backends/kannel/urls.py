from django.urls import include, path
from rapidsms.backends.kannel import views


urlpatterns = (
    path('account/', include('rapidsms.urls.login_logout')),
    path('delivery-report/',
        views.DeliveryReportView.as_view(),
        name='kannel-delivery-report'),
    path('backend/kannel/',
        views.KannelBackendView.as_view(backend_name='kannel-backend'),
        name='kannel-backend'),
)
