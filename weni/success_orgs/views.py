from django.conf import settings

from rest_framework.renderers import JSONRenderer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header

from .business import get_user_success_orgs_by_email, retrieve_success_org, UserDoesNotExist, OrgDoesNotExist
from .serializers import UserSuccessOrgSerializer


class SuccessOrgAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def check_permissions(self, request):

        auth = get_authorization_header(request).split()

        if not auth:
            raise exceptions.NotAuthenticated()

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)

        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        if auth[1].decode() != settings.FIXED_SUPER_ACCESS_TOKEN:
            raise exceptions.PermissionDenied(detail="Invalid token!")

    def get_user_email(request) -> str:
        user_email = request.query_params.get("email")

        if user_email is None:
            raise exceptions.ValidationError("The query param: user_email is required!")

        return user_email

    def get(self, request, **kwargs) -> Response:
        uuid = kwargs.get("uuid")

        if uuid is not None:
            return self.retrieve(request, uuid)

        return self.list(request, **kwargs)

    def list(self, request, **kwargs) -> Response:
        user_email = self.get_user_email(request)

        try:
            user_sucess_orgs = get_user_success_orgs_by_email(user_email)
        except UserDoesNotExist:
            raise exceptions.ValidationError(f"User with email: {user_email} does not exist")

        serializer = UserSuccessOrgSerializer(user_sucess_orgs)

        return Response(serializer.data)

    def retrieve(self, request, uuid) -> Response:
        user_email = self.get_user_email(request)

        try:
            org = retrieve_success_org(user_email, uuid)
        except OrgDoesNotExist:
            raise exceptions.ValidationError(f"Org with UUID: {uuid} does not exist")
        except UserDoesNotExist:
            raise exceptions.ValidationError(f"User with email: {user_email} does not exist")

        serializer = UserSuccessOrgSerializer(org)

        return Response(serializer.data)
