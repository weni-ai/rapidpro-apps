from django.urls import path

from weni.success_orgs.views import ListSuccessOrgAPIView, RetrieveSuccessOrgAPIView


urlpatterns = [
    path("success_orgs", ListSuccessOrgAPIView.as_view(), name="api.v2.success_orgs"),
    path("success_orgs/<str:uuid>", RetrieveSuccessOrgAPIView.as_view(), name="api.v2.success_orgs_retrieve"),
]
