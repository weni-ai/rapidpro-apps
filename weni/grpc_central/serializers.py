from django.contrib.auth.models import User
from rest_framework import relations

from temba.orgs.models import Org


class UserEmailRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="email", queryset=User.objects.all(), **kwargs)


class OrgUUIDRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="uuid", queryset=Org.objects.all(), **kwargs)
