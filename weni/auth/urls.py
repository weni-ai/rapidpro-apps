from django.conf.urls import include, url
from django.urls import path

from weni.auth.views import check_user_legacy, WeniAuthenticationRequestView

urlpatterns = [
    url(r"^oidc/", include("mozilla_django_oidc.urls")),
    url(r"^check-user-legacy/(?P<email>.*\\w+)/$", check_user_legacy, name="check-user-legacy"),
    path("weni/authenticate/<uuid:organization>", WeniAuthenticationRequestView.as_view(), name="weni-org-choose",),
]
