import json
import logging
import uuid
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, unquote, urlparse

import requests

from botocore.exceptions import NoCredentialsError

from django.test import override_settings
from django.urls import clear_url_caches, reverse

from temba.tests import TembaTest
from temba.tests.s3 import S3_SIGNING_SETTINGS
from temba.tickets.models import Ticketer
from temba.tickets.types.mailgun.type import MailgunType
from temba.tickets.types.zendesk.type import ZendeskType
from temba.utils.s3 import regional_client

from weni.s3.services import (
    REASON_INVALID_METADATA,
    REASON_MISSING_METADATA,
    REASON_ORG_MISMATCH,
    REASON_SECRET_MISMATCH,
    REASON_UNKNOWN_TICKETER,
    check_zendesk_callback,
)

COURIER_S3_ENDPOINT = "https://media-bucket.s3.sa-east-1.amazonaws.com"
AWS_SECRET = S3_SIGNING_SETTINGS["AWS_SECRET_ACCESS_KEY"]
FILE_NAME = "a10e5dfe-6071-4b70-9a0f-6d65afaf0e05.jpg"


def setUpModule():
    from temba.api.v2 import urls as api_urls

    if not any(getattr(pattern, "name", None) == "file_callback" for pattern in api_urls.urlpatterns):
        from weni.s3.urls import urlpatterns
        from weni.utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
    clear_url_caches()


def _upstream(status, body=b"hello", content_type="image/jpeg", content_length="5"):
    upstream = Mock()
    upstream.status_code = status
    headers = {}
    if content_type is not None:
        headers["Content-Type"] = content_type
    if content_length is not None:
        headers["Content-Length"] = content_length
    upstream.headers = headers
    upstream.iter_content.return_value = iter([body]) if body else iter([])
    return upstream


@override_settings(**S3_SIGNING_SETTINGS, COURIER_S3_ENDPOINT=COURIER_S3_ENDPOINT)
class WeniFileCallbackTest(TembaTest):
    def setUp(self):
        super().setUp()
        regional_client.cache_clear()
        self.secret = "zendesk-secret"
        self.ticketer = Ticketer.create(
            self.org,
            self.user,
            ZendeskType.slug,
            "Zendesk",
            {"secret": self.secret, "subdomain": "acme"},
        )

    def media_path(self, org=None, name=FILE_NAME):
        org = self.org if org is None else org
        return f"{org.id}/a10e/5dfe/{name}"

    def callback_url(self, path):
        return reverse("file_callback", kwargs={"path": path})

    def metadata_body(self, ticketer=None, secret=None, ticketer_uuid=None):
        ticketer = self.ticketer if ticketer is None else ticketer
        secret = self.secret if secret is None else secret
        ticketer_id = str(ticketer.uuid) if ticketer_uuid is None else ticketer_uuid
        return json.dumps({"metadata": json.dumps({"ticketer": ticketer_id, "secret": secret})})

    def response_bytes(self, response):
        if response.streaming:
            return b"".join(response.streaming_content)
        return response.content

    def post_file(self, path, body=None, content_type="application/json"):
        kwargs = {}
        if body is not None:
            kwargs["data"] = body
            kwargs["content_type"] = content_type
        return self.client.post(self.callback_url(path), **kwargs)

    def assert_signed_fetch(self, mock_get, path):
        mock_get.assert_called_once()
        url = mock_get.call_args.args[0]
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        self.assertEqual("media-bucket.s3.sa-east-1.amazonaws.com", parsed.hostname)
        self.assertEqual(f"/media/{path}", unquote(parsed.path))
        self.assertIn("X-Amz-Signature", query)
        self.assertEqual(["60"], query["X-Amz-Expires"])
        self.assertEqual({"stream": True, "timeout": (5, 30)}, mock_get.call_args.kwargs)

    def assert_log_is_safe(self, logs, *secrets):
        blob = " ".join(logs.output)
        for record in logs.records:
            blob += " " + " ".join(str(value) for value in record.__dict__.values())
        self.assertNotIn("X-Amz-Signature", blob)
        self.assertNotIn(AWS_SECRET, blob)
        for secret in secrets:
            if secret:
                self.assertNotIn(secret, blob)

    def test_serves_object_bytes_from_a_signed_request(self):
        path = self.media_path()
        upstream = _upstream(200, body=b"hello", content_type="image/jpeg", content_length="5")

        with patch("weni.s3.services.requests.get", return_value=upstream) as mock_get:
            with self.assertNoLogs("weni.s3"):
                response = self.post_file(path, self.metadata_body())

        self.assertEqual(200, response.status_code)
        self.assertEqual(b"hello", self.response_bytes(response))
        self.assertEqual("image/jpeg", response["Content-Type"])
        self.assertEqual("5", response["Content-Length"])
        self.assert_signed_fetch(mock_get, path)
        upstream.close.assert_called_once()

    def test_missing_upstream_content_type_defaults_to_octet_stream(self):
        path = self.media_path()
        upstream = _upstream(200, body=b"raw", content_type=None, content_length=None)

        with patch("weni.s3.services.requests.get", return_value=upstream):
            response = self.post_file(path, self.metadata_body())

        self.assertEqual(200, response.status_code)
        self.assertEqual(b"raw", self.response_bytes(response))
        self.assertEqual("application/octet-stream", response["Content-Type"])
        self.assertNotIn("Content-Length", response)

    def test_upstream_failures_return_an_empty_body(self):
        path = self.media_path()
        metadata = self.metadata_body()
        cases = (
            (_upstream(404, body=b"<Code>NoSuchKey</Code>"), 404, "upstream_status", 404),
            (_upstream(403, body=b"<Code>AccessDenied</Code>"), 502, "upstream_status", 403),
            (_upstream(500, body=b"nope"), 502, "upstream_status", 500),
        )
        for upstream, status, field, expected in cases:
            with self.subTest(upstream=upstream.status_code):
                with patch("weni.s3.services.requests.get", return_value=upstream):
                    with self.assertLogs("weni.s3", level="ERROR") as logs:
                        response = self.post_file(path, metadata)

                self.assertEqual(status, response.status_code)
                self.assertEqual(b"", response.content)
                self.assertEqual(1, len(logs.records))
                self.assertEqual(f"media/{path}", logs.records[0].key)
                self.assertEqual(str(self.org.id), logs.records[0].org_id)
                self.assertEqual(expected, getattr(logs.records[0], field))
                upstream.close.assert_called_once()
                self.assert_log_is_safe(logs, metadata, self.secret)

    def test_transport_and_signing_failures_return_502(self):
        path = self.media_path()
        metadata = self.metadata_body()
        cases = (
            ("weni.s3.services.requests.get", requests.Timeout("timed out"), "Timeout"),
            ("weni.s3.services.requests.get", requests.ConnectionError("failed"), "ConnectionError"),
            ("weni.s3.services.presign_url", NoCredentialsError(), "NoCredentialsError"),
        )
        for target, error, error_name in cases:
            with self.subTest(error=error_name):
                with patch(target, side_effect=error) as mocked:
                    with self.assertLogs("weni.s3", level="ERROR") as logs:
                        response = self.post_file(path, metadata)

                self.assertEqual(502, response.status_code)
                self.assertEqual(b"", response.content)
                self.assertEqual(1, len(logs.records))
                self.assertEqual(f"media/{path}", logs.records[0].key)
                self.assertEqual(str(self.org.id), logs.records[0].org_id)
                self.assertEqual(error_name, logs.records[0].error)
                self.assert_log_is_safe(logs, metadata, self.secret)
                if target.endswith("presign_url"):
                    mocked.assert_called_once()

    def test_unsignable_bucket_returns_502_without_fetching(self):
        path = self.media_path()
        with override_settings(COURIER_S3_ENDPOINT="https://other-bucket.s3.sa-east-1.amazonaws.com"):
            with patch("weni.s3.services.requests.get") as mock_get:
                with self.assertLogs("weni.s3", level="ERROR") as logs:
                    response = self.post_file(path, self.metadata_body())

        self.assertEqual(502, response.status_code)
        self.assertEqual(b"", response.content)
        mock_get.assert_not_called()
        self.assertEqual(f"media/{path}", logs.records[0].key)
        self.assertIn("courier media bucket is not signable", logs.output[0])

    def test_invalid_paths_return_404_without_fetching(self):
        org = str(self.org.id)
        for path in (
            f"{org}/ab12//{FILE_NAME}",
            f"{org}/./5dfe/{FILE_NAME}",
            f"{org}/../5dfe/{FILE_NAME}",
            f"{org}/a10e/5dfe/",
        ):
            with self.subTest(path=path):
                with patch("weni.s3.services.requests.get") as mock_get:
                    response = self.post_file(path, self.metadata_body())
                self.assertEqual(404, response.status_code)
                self.assertEqual(b"", response.content)
                mock_get.assert_not_called()

        with patch("weni.s3.services.requests.get") as mock_get:
            response = self.client.post(f"/api/v2/file/{org}/a10e/5dfe/file%.jpg")
        self.assertEqual(404, response.status_code)
        mock_get.assert_not_called()

    def test_authorization_failures_are_logged_and_the_file_is_still_served(self):
        path = self.media_path()
        inactive = Ticketer.create(
            self.org, self.user, ZendeskType.slug, "Inactive", {"secret": self.secret, "subdomain": "old"}
        )
        inactive.is_active = False
        inactive.save(update_fields=("is_active",))
        other = Ticketer.create(self.org, self.user, MailgunType.slug, "Email", {})

        cases = (
            (None, None, REASON_MISSING_METADATA),
            ("{}", "application/json", REASON_MISSING_METADATA),
            (json.dumps({"metadata": "{"}), "application/json", REASON_INVALID_METADATA),
            (self.metadata_body(ticketer_uuid="not-a-uuid"), "application/json", REASON_INVALID_METADATA),
            (self.metadata_body(ticketer_uuid=str(uuid.uuid4())), "application/json", REASON_UNKNOWN_TICKETER),
            (self.metadata_body(ticketer=inactive), "application/json", REASON_UNKNOWN_TICKETER),
            (self.metadata_body(ticketer=other), "application/json", REASON_UNKNOWN_TICKETER),
            (self.metadata_body(secret="wrong-secret"), "application/json", REASON_SECRET_MISMATCH),
            (self.metadata_body(), "application/json", REASON_ORG_MISMATCH),
        )
        for body, content_type, reason in cases:
            request_path = self.media_path(org=self.org2) if reason == REASON_ORG_MISMATCH else path
            with self.subTest(reason=reason):
                upstream = _upstream(200, body=b"hello", content_type="image/jpeg", content_length="5")
                with patch("weni.s3.services.requests.get", return_value=upstream):
                    with self.assertLogs("weni.s3", level="WARNING") as logs:
                        response = self.post_file(request_path, body, content_type)

                self.assertEqual(200, response.status_code)
                self.assertEqual(b"hello", self.response_bytes(response))
                warnings = [record for record in logs.records if record.levelno == logging.WARNING]
                self.assertEqual([reason], [record.reason for record in warnings])
                self.assertEqual(
                    str(self.org2.id if reason == REASON_ORG_MISMATCH else self.org.id), warnings[0].org_id
                )
                posted = body or ""
                self.assert_log_is_safe(logs, self.secret, posted, "wrong-secret")

    def test_get_is_not_allowed(self):
        response = self.client.get(self.callback_url(self.media_path()))
        self.assertEqual(405, response.status_code)

    def test_mailroom_attachment_url_returns_the_object(self):
        path = self.media_path()
        courier_url = f"{COURIER_S3_ENDPOINT}/media/{path}"
        parsed = urlparse(courier_url)
        self.assertTrue(parsed.path.startswith("/media/"))
        relative = parsed.path[len("/media/") :]
        upstream = _upstream(200, body=b"voice-note", content_type="audio/ogg", content_length="10")

        with patch("weni.s3.services.requests.get", return_value=upstream) as mock_get:
            response = self.client.post(
                f"/api/v2/file/{relative}",
                data=self.metadata_body(),
                content_type="application/json",
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual(b"voice-note", self.response_bytes(response))
        self.assertEqual("audio/ogg", response["Content-Type"])
        self.assert_signed_fetch(mock_get, path)

    def test_check_zendesk_callback_reason_codes(self):
        path = self.media_path()
        ok = check_zendesk_callback(self.metadata_body().encode(), "application/json", path)
        self.assertTrue(ok.ok)
        self.assertIsNone(ok.reason)

        missing = check_zendesk_callback(b"", "application/json", path)
        self.assertEqual(REASON_MISSING_METADATA, missing.reason)

        without_key = check_zendesk_callback(b"{}", "text/plain", path)
        self.assertEqual(REASON_MISSING_METADATA, without_key.reason)

        invalid = check_zendesk_callback(json.dumps({"metadata": "[]"}).encode(), "application/json", path)
        self.assertEqual(REASON_INVALID_METADATA, invalid.reason)

        unknown = check_zendesk_callback(
            self.metadata_body(ticketer_uuid=str(uuid.uuid4())).encode(), "application/json", path
        )
        self.assertEqual(REASON_UNKNOWN_TICKETER, unknown.reason)
        self.assertIsNotNone(unknown.ticketer_uuid)

        mismatch = check_zendesk_callback(self.metadata_body(secret="nope").encode(), "application/json", path)
        self.assertEqual(REASON_SECRET_MISMATCH, mismatch.reason)

        other_org = check_zendesk_callback(
            self.metadata_body().encode(), "application/json", self.media_path(self.org2)
        )
        self.assertEqual(REASON_ORG_MISMATCH, other_org.reason)
