from rest_framework import serializers

from temba.channels.models import Channel

class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        #extra_kwargs = {
        #    'uuid': {'write_only': True}
        #}
        model = Channel
        fields = (
            'uuid',
            'name',
            'config',
            'address',
        )