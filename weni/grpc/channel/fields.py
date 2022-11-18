import json

from rest_framework import serializers


class ConfigCharField(serializers.CharField):
    def to_internal_value(self, data):
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            self.fail("invalid", value=data)

    def to_representation(self, value):
        return json.dumps(value)
