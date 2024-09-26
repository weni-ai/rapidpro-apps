from django.urls import path

from rest_framework import routers

from weni.internal.externals.views import ExternalServicesAPIView
from weni.internal.externals.views import PromptViewSet
from weni.internal.externals.views import GenericExternals


urlpatterns = [
    path("externals", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
    path(r"externals/<str:uuid>/", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
]

router = routers.SimpleRouter()

router.register(r'externals/(?P<external_uuid>[^/.]+)/prompts', PromptViewSet, basename='prompts')
router.register("generic/externals", GenericExternals, basename="api.v2.generic.externals")

urlpatterns += router.urls
