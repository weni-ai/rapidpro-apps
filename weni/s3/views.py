import logging

import sentry_sdk

from django.http import HttpResponse, StreamingHttpResponse

from temba.tickets.types.zendesk.views import FileCallbackView
from temba.utils.sentry import scrub_events_for_current_request

from .services import (
    MediaNotFound,
    MediaUnavailable,
    check_zendesk_callback,
    fetch_courier_media,
    iter_courier_media,
    org_id_from_path,
    validate_courier_media_path,
)

logger = logging.getLogger("weni.s3")


class WeniFileCallbackView(FileCallbackView):
    def post(self, request, *args, **kwargs):
        path = kwargs["path"]
        # The body carries the ticketer secret. Keep it out of Sentry events.
        scrub_events_for_current_request()
        org_id = org_id_from_path(path)
        if org_id:
            sentry_sdk.set_tag("org_id", org_id)

        try:
            validate_courier_media_path(path)
        except MediaNotFound:
            return HttpResponse(status=404)

        # Observe mode (phase 1): a failed check is logged and the file is still served.
        # Phase 2 returns 403 here, before any S3 request, once production logs show
        # legitimate Zendesk calls pass.
        auth = check_zendesk_callback(request.body, request.content_type, path)
        if not auth.ok:
            extra = {
                "reason": auth.reason,
                "org_id": org_id,
                "request_content_type": request.content_type,
            }
            if auth.ticketer_uuid:
                extra["ticketer_uuid"] = auth.ticketer_uuid
            logger.warning("zendesk file callback authorization failed", extra=extra)

        try:
            media = fetch_courier_media(path)
        except MediaNotFound:
            return HttpResponse(status=404)
        except MediaUnavailable:
            return HttpResponse(status=502)

        response = StreamingHttpResponse(iter_courier_media(media), content_type=media.content_type)
        if media.content_length is not None:
            response["Content-Length"] = media.content_length
        return response
