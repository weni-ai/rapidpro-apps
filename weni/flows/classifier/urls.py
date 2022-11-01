from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ClassifierEndpoint

router = routers.SimpleRouter()
router.register("flows-backend/classifier", ClassifierEndpoint, basename="api.v2.flows_backend.classifier")

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])