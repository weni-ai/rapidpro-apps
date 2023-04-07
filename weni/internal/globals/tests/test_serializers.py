from unittest.mock import patch, MagicMock

from rest_framework.exceptions import ValidationError, ErrorDetail

from temba.tests import TembaTest
from temba.orgs.models import Org
from temba.globals.models import Global
from weni.internal.globals.serializers import GlobalSerializer


class GlobalSerializerTestCase(TembaTest):
    def setUp(self):
        super().setUp()

        self.global_data = {
            "org": str(self.org.uuid),
            "name": "Fake Global",
            "value": "Sandro",
            "user": self.user.email,
        }

    @patch("django.db.models.query.QuerySet.count")
    def test_exceeding_globals_limit_returns_validation_error(self, mock: MagicMock):
        org_active_globals_limit = self.org.get_limit(Org.LIMIT_GLOBALS)
        mock.return_value = org_active_globals_limit + 1

        message = f"Cannot create a new global as limit is {org_active_globals_limit}."

        with self.assertRaisesMessage(ValidationError, message):
            GlobalSerializer(data=self.global_data).is_valid(raise_exception=True)

    @patch("temba.globals.models.Global.is_valid_name")
    def test_sending_invalid_name_returns_validation_error(self, mock: MagicMock):
        mock.return_value = False

        message = str({"name": [ErrorDetail("Can only contain letters, numbers and hypens.", code="invalid")]})
        with self.assertRaisesMessage(ValidationError, message):
            GlobalSerializer(data=self.global_data).is_valid(raise_exception=True)

    @patch("temba.globals.models.Global.is_valid_key")
    def test_sending_invalid_name_key_returns_validation_error(self, mock: MagicMock):
        mock.return_value = False

        message = str({"name": [ErrorDetail("Isn't a valid name", code="invalid")]})
        with self.assertRaisesMessage(ValidationError, message):
            GlobalSerializer(data=self.global_data).is_valid(raise_exception=True)

    def tests_serializer_successfully_creates_global(self):
        serializer = GlobalSerializer(data=self.global_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(Global.objects.filter(name="Fake Global").exists())
