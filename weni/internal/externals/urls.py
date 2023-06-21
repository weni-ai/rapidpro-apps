from django.urls import path

from weni.internal.externals.views import ExternalServicesAPIView
from weni.internal.externals.views import PromptViewSet

from rest_framework import routers


urlpatterns = [
    path("externals", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
    path(r"externals/<str:uuid>/", ExternalServicesAPIView.as_view(), name="api.v2.externals"),
]

router = routers.SimpleRouter()
router.register(r'externals/(?P<external_uuid>[^/.]+)/prompts', PromptViewSet, basename='prompts')
urlpatterns += router.urls
