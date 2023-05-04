from django.urls import path

from rest_framework import routers

from weni.internal.externals.views import ExternalServicesAPIView
from weni.internal.externals.views import GenericExternals


router = routers.SimpleRouter()
router.register("generic/externals", GenericExternals, basename="api.v2.generic.externals")

urlpatterns = [
    path("externals", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
    path(r"externals/<str:uuid>/", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
]
urlpatterns += router.urls
