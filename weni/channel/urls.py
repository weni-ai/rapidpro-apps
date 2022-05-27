from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ChannelEndpoint

urlpatterns = [
    url(r"^channel/$", ChannelEndpoint.as_view({"get": "list"}), name="api.v2.channel"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
