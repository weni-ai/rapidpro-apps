import celery

from datetime import datetime

from django.shortcuts import get_object_or_404
from django_redis import get_redis_connection
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from weni.internal.authenticators import InternalOIDCAuthentication
from weni.internal.permissions import CanCommunicateInternally
from weni.internal.models import Project


class TemplateMessagesListView(viewsets.ViewSet):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def list(self, request):
        project_uuid = request.query_params.get("project_uuid")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        user_email = request.query_params.get("user")

        org = get_object_or_404(Project, project_uuid=project_uuid)

        # Check if email exists in flows
        try:
            User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response(
                {
                    "detail": f"Error generating report. User: {user_email}, not found in flow"
                },
                status=403,
            )

        # Convert string to datatime object
        start_date_obj = datetime.strptime(start_date, "%m-%d-%Y")
        end_date_obj = datetime.strptime(end_date, "%m-%d-%Y")

        # Convert from datatime object to string
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        end_date_str = end_date_obj.strftime("%Y-%m-%d")

        email_start_date = start_date_obj.strftime("%d/%m/%Y")
        email_end_date = end_date_obj.strftime("%d/%m/%Y")

        lock_key = f"template-messages-lock:{org.id}"
        redis_client = get_redis_connection()
        is_locked = redis_client.get(lock_key)
        data = {
            "project_name": org.name.title(),
            "user_email": user_email,
            "title": f"Relatório de Mensagens Enviadas entre {email_start_date} e {email_end_date}",
            "start_date": start_date_str,
            "end_date": end_date_str,
        }
        kwargs = dict(
            org_id=org.id,
            user=user_email,
            data=data,
        )

        if is_locked:
            return Response(data={"detail": "Request already in process"}, status=409)

        try:
            redis_client.set(lock_key, "locked")
            celery.execute.send_task(
                "generate_sent_report_messages",
                kwargs=kwargs,
            )
        except Exception as e:
            redis_client.delete(f"template-messages-lock:{org.id}")
            return Response(data=e, status=500)

        return Response(status=200)
