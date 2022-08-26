from rest_framework.mixins import CreateModelMixin

from weni.internal.views import InternalGenericViewSet
from weni.internal.flows.serializers import FlowSerializer


class FlowViewSet(CreateModelMixin, InternalGenericViewSet):
    serializer_class = FlowSerializer
