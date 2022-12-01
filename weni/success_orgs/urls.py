from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from weni.success_orgs.views import SuccessOrgAPIView


urlpatterns = [
    path("success_orgs", SuccessOrgAPIView.as_view(), name="api.v2.success_orgs"),
    path("success_orgs/<str:uuid>", SuccessOrgAPIView.as_view(), name="api.v2.success_orgs_retrieve"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
