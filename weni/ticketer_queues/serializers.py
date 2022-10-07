from temba.api.v2.serializers import ReadSerializer
from weni.internal.models import TicketerQueue


class TicketerQueueSerializer(ReadSerializer):
    class Meta:
        model = TicketerQueue
        fields = ("name", "uuid", "created_on")
