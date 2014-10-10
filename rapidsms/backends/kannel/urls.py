from django.conf.urls import patterns, url
from rapidsms.backends.kannel.views import DeliveryReportView


urlpatterns = patterns('',
    url(r"^delivery-report/$", DeliveryReportView.as_view(),
        name="kannel-delivery-report"),
)
