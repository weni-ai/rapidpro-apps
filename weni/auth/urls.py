from django.conf.urls import include, url

from weni.auth.views import check_user_legacy, WeniAuthenticationRequestView

urlpatterns = [
    url(r"^oidc/", include("mozilla_django_oidc.urls")),
    url(r"^check-user-legacy/(?P<email>.*\\w+)/$", check_user_legacy, name="check-user-legacy"),
    url(
        r"^weni/authenticate/(?P<organization>[0-9a-fA-F]{8}-?([0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12})",
        WeniAuthenticationRequestView.as_view(),
        name="weni-org-choose",
    ),
]
