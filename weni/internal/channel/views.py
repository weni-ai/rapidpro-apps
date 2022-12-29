import inspect

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from weni.internal.views import InternalGenericViewSet
from django.conf import settings

from temba.channels.models import Channel
from temba.channels.types import TYPES

from .serializers import ChannelSerializer, CreateChannelSerializer, ChannelWACSerializer

User = get_user_model()

class ChannelEndpoint(viewsets.ModelViewSet, InternalGenericViewSet):
    serializer_class = ChannelSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        channel_type = self.request.query_params.get("channel_type")
        org = self.request.query_params.get("org")

        queryset = Channel.objects.all()

        if channel_type is not None:
            return queryset.filter(channel_type=channel_type)

        if org is not None:
            return queryset.filter(org__uuid=org)

        return queryset

    def retrieve(self, request, uuid=None):
        try:
            channel = Channel.objects.get(uuid=uuid)
        except Channel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(data=self.get_serializer(channel).data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = CreateChannelSerializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, uuid=None):
        channel = get_object_or_404(Channel, uuid=uuid)
        user = get_object_or_404(User, email=request.data.get("user"))

        channel.release(user)

        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def create_wac(self, request):
        serializer = ChannelWACSerializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


class AvailableChannels(viewsets.ViewSet, InternalGenericViewSet):

    def list(self, request):
        types_available = TYPES
        channel_types = {}
        for value in types_available:
            if value not in settings.DISABLED_CHANNELS_INTEGRATIONS:
                fields_types = {}
                attibutes_type =  extract_type_info(types_available[value])
                if not (attibutes_type):
                    return Response(status=status.HTTP_404_NOT_FOUND)

                fields_types['attributes'] = attibutes_type
                channel_types[value] = fields_types

        payload = {
            "channel_types": channel_types,
        }
        return Response(payload)

    def retrieve(self, request, pk=None):
        channel_type = None
        fields_form = {}
        code_type =  pk
        current_form = None
        if code_type:
            channel_type = TYPES.get(code_type.upper(), None)

        if channel_type is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        fields_in_form = []
        if channel_type.claim_view:
            if channel_type.claim_view.form_class:
                current_form = channel_type.claim_view.form_class
            elif channel_type.claim_view.ClaimForm:
                current_form = channel_type.claim_view.ClaimForm

            if current_form:
                form = current_form.base_fields
                for field in form:
                    fields_in_form.append(extract_form_info(form[field], field))

                if not (fields_in_form):
                    return Response(status=status.HTTP_404_NOT_FOUND)

                fields_form['form'] = fields_in_form

            fields_types = {}
            attibutes_type =  extract_type_info(channel_type)
            if not (attibutes_type):
                return Response(status=status.HTTP_404_NOT_FOUND)

            fields_types['attributes'] = attibutes_type

        payload = {
            "attributes": fields_types.get('attributes'),
            "form": fields_form.get('form')
        }

        return Response(payload)


def extract_type_info(_class):
    channel = {}
    type_exclude = ["<class 'function'>"]
    items_exclude = ["redact_response_keys", "claim_view_kwargs", 
                     "extra_links", "redact_request_keys"]

    for i in _class.__class__.__dict__.items():
        if not i[0].startswith('_'):
            if not inspect.isclass(i[1]) and str(type(i[1])) not in(type_exclude) \
                and i[0] not in items_exclude:
                if str(type(i[1])) == "<enum 'Category'>":
                    channel[i[0]] = {"name": i[1].name if i[1].name else "",
                                    "value": i[1].value if i[1].value else ""}

                elif i[0] == "configuration_urls":
                    if i[1]:
                        if i[1][0]:
                            urls_list = []
                            url_dict = {}
                            for url in i[1]:
                                if url.get('label'):
                                    url_dict['label'] = str(url.get('label'))

                                if i[1][0].get('url'):
                                    url_dict['url'] = str(url.get('url'))

                                if i[1][0].get('description'):
                                    url_dict['description'] = str(url.get('description'))

                            urls_list.append(url_dict)
                            channel[i[0]] = urls_list

                elif i[0] == "configuration_blurb":
                    channel[i[0]] = str(i[1])

                elif i[0] == "claim_blurb":
                    channel[i[0]] = str(i[1])

                elif (i[0]) == "ivr_protocol":
                    channel[i[0]] = {"name": i[1].name if i[1].name else "", 
                                    "value": i[1].value if i[1].value else ""}
                else:
                    channel[i[0]] = (i[1])

    if (not (channel.get('code'))) or (not (len(channel))>0) \
        or (not (channel.get('name'))):
        return None

    channel['num_fields'] = len(channel)
    return ((channel))

def extract_form_info(_form, name_form):
    detail = {}
    detail['name'] = name_form if name_form else None

    try:
        detail['type'] = str(_form.widget.input_type)
    except AttributeError:
        detail['type'] = str(_form.widget.__class__.__name__).lower()

    if _form.help_text:
        detail['help_text'] = str(_form.help_text)
    else:
        detail['help_text'] = ''

    if detail.get('type') == 'select':
        detail['choices'] = _form.choices

    if _form.label:
        detail['label'] = str(_form.label)
    else:
        detail['label'] = ''

    if not (detail.get('name')) or not (detail.get('type')):
        return None

    return detail
