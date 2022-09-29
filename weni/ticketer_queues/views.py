from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from weni.internal.models import TicketerQueue
from weni.ticketer_queues.serializers import TicketerQueueSerializer


class TicketerQueuesEndpoint(APIView):
    """
    List ticketer queues
    """

    queryset = TicketerQueue.objects.all()
    serializer_class = TicketerQueueSerializer

    def get(self, request, format=None):
        params = self.request.query_params

        ticketer_uuid = params.get("ticketer_uuid")

        if ticketer_uuid is None:
            raise ValidationError("ticketer_uuid is required")

        queues = TicketerQueue.objects.filter(ticketer__uuid=ticketer_uuid)

        serializer = TicketerQueueSerializer(queues, many=True)
        return Response(serializer.data)
