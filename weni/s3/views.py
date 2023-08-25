import requests

from django.http import HttpResponse
from django.conf import settings

from temba.tickets.types.zendesk.views import FileCallbackView


class WeniFileCallbackView(FileCallbackView):
    def post(self, request, *args, **kwargs):
        path = "media/" + kwargs["path"]
        assert ".." not in kwargs["path"]

        url = f"{settings.COURIER_S3_ENDPOINT}/{path}"

        response = requests.get(url)
        file_type = response.headers.get("Content-Type")

        return HttpResponse(response.content, content_type=file_type)
