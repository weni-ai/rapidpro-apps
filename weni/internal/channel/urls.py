from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ChannelEndpoint

router = routers.SimpleRouter()
router.register("channel", ChannelEndpoint, basename="channel")

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])
