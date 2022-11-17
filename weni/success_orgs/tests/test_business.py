from django.test import TestCase
from django.contrib.auth import get_user_model

from weni.success_orgs.business import UserDoesNotExist, get_user_by_email


User = get_user_model()


class GetUserByEmailTestCase(TestCase):
    def setUp(self) -> None:
        self.user_email = "fake@weni.ai"
        self.user = User.objects.create(email=self.user_email)

    def test_get_user_by_email(self):
        user = get_user_by_email(self.user_email)
        self.assertEqual(user.email, self.user_email)

    def test_get_user_by_email_raise_does_not_exist_exception_with_wrong_email(self):
        with self.assertRaises(UserDoesNotExist):
            user = get_user_by_email("wrong@weni.ai")
