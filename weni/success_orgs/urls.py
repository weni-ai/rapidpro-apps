from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from weni.success_orgs.views import ListSuccessOrgAPIView, RetrieveSuccessOrgAPIView


urlpatterns = [
    path("success_orgs", ListSuccessOrgAPIView.as_view(), name="api.v2.success_orgs"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])

urlpatterns.append(
    path("success_orgs/<str:uuid>", RetrieveSuccessOrgAPIView.as_view(), name="api.v2.success_orgs_retrieve"),
)
