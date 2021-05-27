from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from weni.template_message.views import TemplateMessageView


urlpatterns = [
    path("template_messages", TemplateMessageView.as_view(), name="api.v2.template_messages")
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])