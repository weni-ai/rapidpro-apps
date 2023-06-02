from django.contrib.auth.models import User
from rest_framework import relations
from rest_framework import serializers

from temba.orgs.models import Org


class UserEmailRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="email", queryset=User.objects.all(), **kwargs)


class OrgUUIDRelatedField(relations.SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="uuid", queryset=Org.objects.all(), **kwargs)


class SerializerMethodCharField(serializers.CharField):
    """
    Read and write class, using custom methods.
    behaves similarly to SerializerMethodField, however he allow create.
    """

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        # The method name defaults to `get_{field_name}`.
        if self.method_name is None:
            self.method_name = "get_{field_name}".format(field_name=field_name)

        super().bind(field_name, parent)

    def get_attribute(self, instance):
        method = getattr(self.parent, self.method_name)
        return method(instance)
