from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ChannelEndpoint

router = routers.SimpleRouter()
router.register("flows-backend/channel", ChannelEndpoint, basename="api.v2.flows_backend.channel")

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])
