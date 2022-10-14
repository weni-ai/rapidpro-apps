from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ChannelEndpoint, AvailableChannels

router = routers.SimpleRouter()
router.register("flows-backend/channel", ChannelEndpoint, basename="api.v2.flows_backend.channel")
router.register("flows-backend/channels", AvailableChannels, basename="api.v2.flows_backend.channels")

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])
