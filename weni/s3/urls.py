from django.conf.urls import url

from .views import WeniFileCallbackView


urlpatterns = [
    url(
        r"^file/(?P<path>[\w\-./]+)$",
        WeniFileCallbackView.as_view(),
        name="file_callback",
    ),
]
