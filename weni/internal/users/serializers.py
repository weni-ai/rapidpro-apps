from rest_framework import serializers

from weni import serializers as weni_serializers


class UserAPITokenSerializer(serializers.Serializer):
    user = weni_serializers.UserEmailRelatedField(required=True)
    org = weni_serializers.OrgUUIDRelatedField(required=True)
