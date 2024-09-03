from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

from temba.globals.models import Global
from temba.orgs.models import Org
from weni.internal.models import Project
from weni.internal.views import InternalGenericViewSet
from weni.internal.globals.serializers import GlobalSerializer


class GlobalViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    InternalGenericViewSet,
):
    serializer_class = GlobalSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        queryset = Global.objects.filter(is_active=True)
        org = self.request.query_params.get("org")

        try:
            org_object = Org.objects.get(uuid=org)
            queryset = queryset.filter(org=org_object)
            return queryset

        except Org.DoesNotExist as error:
            raise ValidationError(detail={"message": str(error)})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer.validated_data)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, validated_data_list):
        self.get_serializer().create_many(validated_data_list)

    @action(detail=False, methods=["delete"])
    def delete(self, request, *args, **kwargs):
        org_uuid = request.data.get("org")
        key = request.data.get("key")
        user = request.user
        project_uuid = request.data.get("project_uuid")

        if not org_uuid and not project_uuid:
            raise ValidationError({"detail": "org or project_uuid is required to delete the object."})

        if not key:
            raise ValidationError({"detail": "key is required to delete the object."})

        if org_uuid:
            try:
                org_object = Org.objects.get(uuid=org_uuid)
            except Org.DoesNotExist:
                raise ValidationError({"detail": "Organization not found."})

            instance = get_object_or_404(Global, key=key, org=org_object, is_active=True)

            self.perform_destroy(instance, user)

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if project_uuid:
            try:
                project_object = Project.objects.get(project_uuid=project_uuid)
            except Project.DoesNotExist:
                raise ValidationError({"detail": "Project not found."})

            instance = get_object_or_404(Global, key=key, org=project_object.org, is_active=True)

            self.perform_destroy(instance, user)

            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, user):
        instance.is_active = False
        instance.modified_by = user
        instance.save()


class GlobalRetailViewSet(InternalGenericViewSet):
    def create(self, request, *args, **kwargs):
        project_uuid = request.data.get("project_uuid")
        name = request.data.get("name")
        value = request.data.get("value")
        user_email = request.data.get("user")

        if not project_uuid:
            raise ValidationError({"detail": "Project_uuid is required to create the object."})
        
        if not name:
            raise ValidationError({"detail": "Name is required to create the object."})
        
        if not value:
            raise ValidationError({"detail": "Value is required to create the object."})
        
        if not user_email:
            raise ValidationError({"detail": "User is required to create the object."})
        
        user = get_object_or_404(User, email=user_email)
        
        project = get_object_or_404(Project, project_uuid=project_uuid)
        
        project_active_globals_limit = project.get_limit(project.LIMIT_GLOBALS)

        if project.globals.filter(is_active=True).count() >= project_active_globals_limit:
            raise ValidationError(f"Cannot create a new global as limit is {project_active_globals_limit}.")

        if not Global.is_valid_name(name):
            raise ValidationError("Can only contain letters, numbers and hypens.")
 

        if not Global.is_valid_key(Global.make_key(name)):
            raise ValidationError("Isn't a valid name")
        
        key = Global.make_key(name=name)
        
        global_instance= Global.get_or_create(
            project,
            user,
            key,
            name,
            value
        )

        response = {
            "project_uuid":global_instance.org.proj_uuid,
            "key":global_instance.key,
            "value":global_instance.value
        }
    
        return Response(response, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["delete"])
    def delete(self, request, *args, **kwargs):
        key = request.data.get("key")
        user = request.user
        project_uuid = request.data.get("project_uuid")

        if not project_uuid:
            raise ValidationError({"detail": "project_uuid is required to delete the object."})
        if not key:
            raise ValidationError({"detail": "key is required to delete the object."})

        try:
            project_object = Project.objects.get(project_uuid=project_uuid)
        except Project.DoesNotExist:
            raise ValidationError({"detail": "Project not found."})

        instance = get_object_or_404(Global, key=key, org=project_object.org, is_active=True)

        self.perform_destroy(instance, user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, user):
        instance.is_active = False
        instance.modified_by = user
        instance.save()
