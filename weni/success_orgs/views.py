from django.conf import settings
from django.http import Http404
from django.core import exceptions as django_exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions as drf_exceptions
from rest_framework.authentication import get_authorization_header


from weni.internal.authenticators import InternalOIDCAuthentication
from .business import (
    get_user_success_orgs_by_email,
    retrieve_success_org,
    user_has_org_permission,
    UserDoesNotExist,
    OrgDoesNotExist,
)
from .serializers import UserSuccessOrgSerializer, SuccessOrgSerializer


class ListSuccessOrgAPIView(APIView):

    renderer_classes = [JSONRenderer]
    authentication_classes = []
    permission_classes = []

    def check_permissions(self, request):

        auth = get_authorization_header(request).split()

        if not auth:
            raise drf_exceptions.NotAuthenticated()

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise drf_exceptions.AuthenticationFailed(msg)

        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise drf_exceptions.AuthenticationFailed(msg)

        if auth[1].decode() != settings.FIXED_SUPER_ACCESS_TOKEN:
            raise drf_exceptions.PermissionDenied(detail="Invalid token!")

    def get_user_email(self, request) -> str:
        user_email = request.query_params.get("email")

        if user_email is None:
            raise exceptions.ValidationError("The query param: user_email is required!")

        return user_email

    def get(self, request, **kwargs) -> Response:
        user_email = self.get_user_email(request)

        try:
            user_sucess_orgs = get_user_success_orgs_by_email(user_email)
        except UserDoesNotExist:
            raise exceptions.ValidationError(f"User with email: {user_email} does not exist")

        serializer = UserSuccessOrgSerializer(user_sucess_orgs)

        return Response(serializer.data)


class RetrieveSuccessOrgAPIView(APIView):

    authentication_classes = [InternalOIDCAuthentication]
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def get(self, request, uuid) -> Response:

        try:
            org = retrieve_success_org(uuid)
        except OrgDoesNotExist:
            raise Http404
        except django_exceptions.ValidationError as error:
            raise drf_exceptions.ValidationError(error.messages)

        if not user_has_org_permission(request.user, org):
            raise Http404

        serializer = SuccessOrgSerializer(org)

        return Response(serializer.data)
