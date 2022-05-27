from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins
from .serializers import ChannelSerializer

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.contacts.models import Contact, ContactGroup
from temba.orgs.models import Org
from temba.flows.models import FlowRun
from temba.utils import str_to_bool
from rest_framework import status

from temba.channels.models import Channel

from django.contrib.auth.models import User

class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass

class ChannelEndpoint(CreateListRetrieveViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    
    def create_channel_end(self, request, *args, **kwargs):

        data: dict = None

        try:
            data = json.loads(request.data.get("data"))
        except json.decoder.JSONDecodeError:
            self.context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Can't decode the `data` field")

        user = get_object_or_404(User, email=request.data.get("user"))
        org = get_object_or_404(Org, uuid=request.data.get("org"))

        channel_type = TYPES.get(request.data.get("channeltype_code"), None)

        if channel_type is None:
            channel_type_code = request.data.get("channeltype_code")
            raise Http404(f"No channels found with '{channel_type_code}' code")

        url = self.create_channel(user, org, data, channel_type)

        if url is None:
            self.context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Bad Request")

        if "/users/login/?next=" in url:
            self.context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, f"User: {user.email} do not have permission in Org: {org.uuid}"
            )

        regex = "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
        channe_uuid = re.findall(regex, url)[0]
        channel = Channel.objects.get(uuid=channe_uuid)

        return channel_pb2.Channel(
            uuid=channe_uuid, name=channel.name, address=channel.address, config=json.dumps(channel.config)
        )

        return Response(status=status.HTTP_200_OK)


    def create_channel(self, user: User, org: Org, data: dict, channel_type) -> str:
        factory = RequestFactory()
        url = f"channels/types/{channel_type.slug}/claim"

        request = factory.post(url, data)
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        user._org = org
        request.user = user
        response = MessageMiddleware(channel_type.claim_view.as_view(channel_type=channel_type))(request)

        if isinstance(response, HttpResponseRedirect):
            return response.url
    