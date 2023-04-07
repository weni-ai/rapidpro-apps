from django.urls import path
from weni.internal.externals.views import ExternalServicesAPIView


urlpatterns = [
    path("externals", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
]
