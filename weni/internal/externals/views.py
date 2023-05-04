
import inspect

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import ViewSet

from weni.internal.authenticators import InternalOIDCAuthentication
from weni.internal.permissions import CanCommunicateInternally
from weni.internal.externals.serializers import ExternalServicesSerializer
from temba.externals.models import ExternalService

from temba.externals.types import TYPES

from weni.internal.views import InternalGenericViewSet

if TYPE_CHECKING:
    from rest_framework.request import Request


class ExternalServicesAPIView(APIView):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def post(self, request: "Request") -> Response:
        serializer = ExternalServicesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, uuid=None):
        external_service = get_object_or_404(ExternalService, uuid=uuid)
        user = get_object_or_404(User, email=request.query_params.get("user"))

        external_service.release(user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GenericExternals(ViewSet, InternalGenericViewSet):
    lookup_field = 'type'

    def list(self, request):
        external_types = {}
        for value in TYPES:
            fields_types = {}
            attributes_type = extract_type_info(TYPES[value])
            if not attributes_type:
                return Response(status=status.HTTP_404_NOT_FOUND)

            fields_types['attributes'] = attributes_type
            external_types[value] = fields_types

        payload = {
            "external_types": external_types,
        }
        return Response(payload)

    def retrieve(self, request, type=None):
        external_type = TYPES.get(type, None)
        if not external_type:
            return Response(status=status.HTTP_404_NOT_FOUND)

        fields_form = {}
        fields_in_form = []
        if external_type.connect_view and external_type.connect_view.form_class:
            form = external_type.connect_view.form_class.base_fields
            for field in form:
                fields_in_form.append(extract_form_info(form[field], field))

            if not fields_in_form:
                return Response(status=status.HTTP_404_NOT_FOUND)

            fields_form['form'] = fields_in_form

        fields_types = {}
        attributes_type = extract_type_info(external_type)
        if not attributes_type:
            return Response(status=status.HTTP_404_NOT_FOUND)

        fields_types['attributes'] = attributes_type

        payload = {
            "attributes": fields_types.get('attributes'),
            "form": fields_form.get('form')
        }

        return Response(payload)


def extract_type_info(cls):
    """
    Extracts information about a class instance.

    Parameters:
        cls (object): An instance of a class.

    Returns:
        dict: A dictionary containing information about the class instance.
    """
    excluded_types = {"<class 'function'>"}
    excluded_items = {"CONFIG_APP_KEY", "CONFIG_APP_SECRET", "connect_blurb", "icon"}
    info = {}

    for name, value in cls.__class__.__dict__.items():
        if name.startswith("_") or inspect.isclass(value) \
                or str(type(value)) in excluded_types or name in excluded_items:
            continue

        info[name] = value

    if not info or "name" not in info:
        return None

    return info


def extract_form_info(form, name_form):
    """
    Extracts information about a form field.

    Parameters:
        form (django.forms): The form field to extract information from.
        name_form (str): The name of the form field.

    Returns:
        dict: A dictionary containing information about the form field.
    """
    detail = {}
    detail["name"] = name_form if name_form else None

    try:
        detail["type"] = str(form.widget.input_type)
    except AttributeError:
        detail["type"] = None

    detail["help_text"] = str(form.help_text) if form.help_text else None

    if detail.get("type") == "select":
        detail["choices"] = form.choices

    detail["label"] = str(form.label) if form.label else None

    if not detail.get("name") or not detail.get("type"):
        return None

    return detail
