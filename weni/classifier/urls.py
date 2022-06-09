from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ClassifierEndpoint

urlpatterns = [
    url(r"^classifier/$", ClassifierEndpoint.as_view({"get": "list"}), name="api.v2.classifier"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])