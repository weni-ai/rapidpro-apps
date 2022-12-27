import requests

import magic
from django.http import HttpResponse
from django.conf import settings

from temba.tickets.types.zendesk.views import FileCallbackView


class WeniFileCallbackView(FileCallbackView):

    def post(self, request, *args, **kwargs):
        path = "media/" + kwargs["path"]
        assert ".." not in kwargs["path"]

        url = f"{settings.COURIER_S3_ENDPOINT}/{path}"

        file = requests.get(url).content
        file_type = magic.from_buffer(file, mime=True)

        return HttpResponse(file, content_type=file_type)
