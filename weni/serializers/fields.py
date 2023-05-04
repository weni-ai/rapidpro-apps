from django.contrib.auth import get_user_model
from rest_framework import relations

from temba.orgs.models import Org
from weni.internal.models import Project


User = get_user_model()


class UserEmailRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="email", queryset=User.objects.all(), **kwargs)


class OrgUUIDRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="uuid", queryset=Org.objects.all(), **kwargs)


class ProjectUUIDRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="project_uuid", queryset=Project.objects.all(), **kwargs)
