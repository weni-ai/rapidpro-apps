from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from weni.internal.views import InternalGenericViewSet
from weni.internal.orgs.serializers import OrgSerializer

from temba.orgs.models import Org


class OrgViewSet(ModelViewSet, InternalGenericViewSet):
    serializer_class = OrgSerializer

    @action(detail=False, methods=['DELETE'])
    def pre_destroy(self, request):

        user = get_object_or_404(User, pk=request.data.get("user"))
        org = get_object_or_404(Products, pk=request.data.get("org"))

        if user.id and user.id > 0 and hasattr(org, "modified_by_id"):
            org.modified_by = user

            # Interim fix, remove after implementation in the model.
            org.save(update_fields=["modified_by"])

    @action(detail=False, methods=['GET'])
    def get_user(self, request):
        user_email = request.query_params.get("user_email")

        if not user_email:
            self.context.abort(grpc.StatusCode.NOT_FOUND, "Email cannot be null")

        try:
            return User.objects.get(email=request.query_params.get("user_email"))
        except User.DoesNotExist:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"User:{request.query_params.get("user_email")} not found!")

    @action(detail=False, methods=['GET'])
    def _user_has_permisson(self, user: User, org: Org):
        return Response(
            data=(
                user.org_admins.filter(pk=org.pk)
                or user.org_viewers.filter(pk=org.pk)
                or user.org_editors.filter(pk=org.pk)
                or user.org_surveyors.filter(pk=org.pk)
            )
        )

    @action(detail=False, methods=['GET'])
    def get_orgs(self, user: User):

        user = get_object_or_404(User, pk=request.query_params.get("user"))

        admins = user.org_admins.filter(is_active=True)
        viewers = user.org_viewers.filter(is_active=True)
        editors = user.org_editors.filter(is_active=True)
        surveyors = user.org_surveyors.filter(is_active=True)

        return Response(data={"data": admins.union(viewers, editors, surveyors)})
