from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ChannelEndpoint, AvailableChannels


router = routers.SimpleRouter()
router.register("channel", ChannelEndpoint, basename="channel")
router.register("channels", AvailableChannels, basename="channels")

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])
