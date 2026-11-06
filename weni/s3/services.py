import hmac
import logging
import uuid

import requests
from botocore.exceptions import BotoCoreError, ClientError

from django.conf import settings

from temba.tickets.types.zendesk.type import ZendeskType
from temba.utils import json
from temba.utils.s3 import parse_s3_url, presign_url, signable_buckets

from .repositories import get_active_zendesk_ticketer

logger = logging.getLogger("weni.s3")

COURIER_MEDIA_KEY_PREFIX = "media/"
MEDIA_FETCH_URL_EXPIRES = 60
MEDIA_FETCH_CONNECT_TIMEOUT = 5
MEDIA_FETCH_READ_TIMEOUT = 30
MEDIA_STREAM_CHUNK_SIZE = 64 * 1024

REASON_MISSING_METADATA = "missing_metadata"
REASON_INVALID_METADATA = "invalid_metadata"
REASON_UNKNOWN_TICKETER = "unknown_ticketer"
REASON_SECRET_MISMATCH = "secret_mismatch"
REASON_ORG_MISMATCH = "org_mismatch"


class MediaNotFound(Exception):
    """The object key is malformed or S3 reports that it does not exist."""


class MediaUnavailable(Exception):
    """S3, signing, or the bucket configuration cannot serve the object."""


class CourierMedia:
    def __init__(self, stream, content_type, content_length):
        self.stream = stream
        self.content_type = content_type
        self.content_length = content_length


class CallbackAuthResult:
    def __init__(self, ok, reason=None, ticketer_uuid=None):
        self.ok = ok
        self.reason = reason
        self.ticketer_uuid = ticketer_uuid


def validate_courier_media_path(path):
    """
    Reject an empty, "." or ".." segment before any database or S3 access.
    """
    if any(segment in ("", ".", "..") for segment in path.split("/")):
        raise MediaNotFound()


def object_key(path):
    return f"{COURIER_MEDIA_KEY_PREFIX}{path}"


def org_id_from_path(path):
    return path.split("/", 1)[0]


def check_zendesk_callback(body, content_type, path):
    """
    Evaluate the metadata Zendesk posts. Never raises on malformed input.
    ``content_type`` is part of the call so the view can log the encoding it received;
    a different encoding still parses when the body is JSON.
    """
    payload = _json_object(body)
    if payload is None or not isinstance(payload.get("metadata"), str):
        return CallbackAuthResult(ok=False, reason=REASON_MISSING_METADATA)

    metadata = _json_object(payload["metadata"])
    ticketer_uuid = metadata.get("ticketer") if metadata is not None else None
    secret = metadata.get("secret") if metadata is not None else None
    if not isinstance(ticketer_uuid, str) or not isinstance(secret, str):
        return CallbackAuthResult(ok=False, reason=REASON_INVALID_METADATA)

    parsed_uuid = _parse_uuid(ticketer_uuid)
    if parsed_uuid is None:
        return CallbackAuthResult(ok=False, reason=REASON_INVALID_METADATA)

    ticketer = get_active_zendesk_ticketer(parsed_uuid)
    if ticketer is None:
        return CallbackAuthResult(ok=False, reason=REASON_UNKNOWN_TICKETER, ticketer_uuid=parsed_uuid)

    configured = ticketer.config.get(ZendeskType.CONFIG_SECRET) if isinstance(ticketer.config, dict) else None
    if not isinstance(configured, str) or not hmac.compare_digest(configured, secret):
        return CallbackAuthResult(ok=False, reason=REASON_SECRET_MISMATCH, ticketer_uuid=parsed_uuid)

    if org_id_from_path(path) != str(ticketer.org_id):
        return CallbackAuthResult(ok=False, reason=REASON_ORG_MISMATCH, ticketer_uuid=parsed_uuid)

    return CallbackAuthResult(ok=True, ticketer_uuid=parsed_uuid)


def fetch_courier_media(path):
    """
    Validate ``path``, presign the Courier media object and fetch it.
    Raises MediaNotFound or MediaUnavailable.
    """
    validate_courier_media_path(path)
    key = object_key(path)
    org_id = org_id_from_path(path)
    canonical_url = f"{settings.COURIER_S3_ENDPOINT.rstrip('/')}/{key}"

    # presign_url returns the URL unchanged when the bucket is not one it signs,
    # which would send the unsigned GET this callback exists to stop.
    location = parse_s3_url(canonical_url)
    if location is None or location.bucket not in signable_buckets():
        logger.error("courier media bucket is not signable", extra={"key": key, "org_id": org_id})
        raise MediaUnavailable()

    try:
        signed_url = presign_url(canonical_url, expires=MEDIA_FETCH_URL_EXPIRES)
    except (BotoCoreError, ClientError) as exc:
        logger.exception(
            "zendesk file callback signing failed",
            extra={"key": key, "org_id": org_id, "error": type(exc).__name__},
        )
        raise MediaUnavailable() from exc

    try:
        upstream = requests.get(
            signed_url,
            stream=True,
            timeout=(MEDIA_FETCH_CONNECT_TIMEOUT, MEDIA_FETCH_READ_TIMEOUT),
        )
    except (requests.Timeout, requests.ConnectionError) as exc:
        # The exception text includes the signed URL, so log only the class name.
        logger.error(
            "zendesk file callback media fetch failed",
            extra={"key": key, "org_id": org_id, "error": type(exc).__name__},
        )
        raise MediaUnavailable() from None

    if upstream.status_code == 200:
        content_type = upstream.headers.get("Content-Type") or "application/octet-stream"
        return CourierMedia(upstream, content_type, upstream.headers.get("Content-Length"))

    status = upstream.status_code
    upstream.close()
    if status == 404:
        logger.error(
            "zendesk file callback media missing",
            extra={"key": key, "org_id": org_id, "upstream_status": status},
        )
        raise MediaNotFound()

    logger.error(
        "zendesk file callback media unavailable",
        extra={"key": key, "org_id": org_id, "upstream_status": status},
    )
    raise MediaUnavailable()


def iter_courier_media(media):
    try:
        for chunk in media.stream.iter_content(chunk_size=MEDIA_STREAM_CHUNK_SIZE):
            if chunk:
                yield chunk
    finally:
        media.stream.close()


def _json_object(raw):
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, UnicodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _parse_uuid(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError, TypeError):
        return None
