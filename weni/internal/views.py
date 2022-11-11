from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from weni.internal.authenticators import InternalOIDCAuthentication
from weni.internal.permissions import CanCommunicateInternally


class InternalGenericViewSet(GenericViewSet):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []
