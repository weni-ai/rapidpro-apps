from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ChannelEndpoint

router = routers.SimpleRouter()
router.register("flows-backend/channel", ChannelEndpoint, basename="api.v2.flows_backend.channel")

urlpatterns = [
    #url(r'^flows-backend/channel/$', 'api.v2.flows_backend.channel'),
    #url(r"^flows-backend/channel/", ChannelEndpoint.as_view({"get": "list"}), name="api.v2.flows_backend.channel"),
    #url(r"^flows-backend/channel/(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/", ChannelEndpoint.as_view(), name="api.v2.flows_backend.channel"),
]

#print(router.urls)

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])
