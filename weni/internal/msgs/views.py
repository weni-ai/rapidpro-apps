import celery
import pytz

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

        # Validate if the email exists in flows
        if not self.is_valid_user(user_email):
            return Response(
                {
                    "detail": f"Error generating report. User: {user_email}, not found in flow"
                },
                status=403,
            )

        # Convert string dates to datetime objects and handle timezone
        start_date_utc, end_date_utc, email_start_date, email_end_date = (
            self.convert_dates_with_timezone(start_date, end_date, org.timezone)
        )

        lock_key = f"template-messages-lock:{org.id}"
        redis_client = get_redis_connection()
        is_locked = redis_client.get(lock_key)

        if is_locked:
            return Response(data={"detail": "Request already in process"}, status=409)

        data = {
            "project_name": org.name.title(),
            "user_email": user_email,
            "title": f"Relatório de Mensagens Enviadas entre {email_start_date} e {email_end_date}",
            "start_date": start_date_utc,
            "end_date": end_date_utc,
        }

        kwargs = dict(
            org_id=org.id,
            user=user_email,
            data=data,
        )

        try:
            celery.execute.send_task(
                "generate_sent_report_messages",
                kwargs=kwargs,
            )
        except Exception as e:
            redis_client.delete(f"template-messages-lock:{org.id}")
            return Response(data=str(e), status=500)

        return Response(status=200)

    def is_valid_user(self, email):
        try:
            User.objects.get(email=email)
            return True
        except User.DoesNotExist:
            return False

    def convert_dates_with_timezone(self, start_date, end_date, org_timezone):
        # Fallback to UTC if the client's timezone is not set
        client_timezone = pytz.timezone(str(org_timezone) if org_timezone else "UTC")

        # Convert start and end dates to datetime objects
        start_date_obj = datetime.strptime(start_date, "%m-%d-%Y")
        end_date_obj = datetime.strptime(end_date, "%m-%d-%Y")

        # Localize the dates to the client's timezone
        start_date_client = client_timezone.localize(
            datetime.combine(start_date_obj, datetime.min.time())
        )
        end_date_client = client_timezone.localize(
            datetime.combine(end_date_obj, datetime.max.time())
        )

        # Convert dates to UTC
        start_date_utc = start_date_client.astimezone(pytz.UTC).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        end_date_utc = end_date_client.astimezone(pytz.UTC).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        email_start_date = start_date_obj.strftime("%d/%m/%Y")
        email_end_date = end_date_obj.strftime("%d/%m/%Y")

        return start_date_utc, end_date_utc, email_start_date, email_end_date
