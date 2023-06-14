from datetime import datetime

from django.db import connection

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from weni.internal.authenticators import InternalOIDCAuthentication
from weni.internal.permissions import CanCommunicateInternally


class TemplateMessagesListView(viewsets.ViewSet):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def list(self, request):
        org_id = request.query_params.get("org_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Convert string to datatime object
        start_date_obj = datetime.strptime(start_date, "%m-%d-%Y")
        end_date_obj = datetime.strptime(end_date, "%m-%d-%Y")

        # Convert from datatime object to string
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        end_date_str = end_date_obj.strftime("%Y-%m-%d")

        with connection.cursor() as cursor:
            query = f"""
                SELECT
                    template.name AS "Template",
                    flow.name AS "Fluxos Utilizados",
                    COUNT(msg.id) AS "Total por Template"
                FROM
                    public.msgs_msg AS msg
                    INNER JOIN public.templates_template AS template
                        ON CAST(template.uuid AS text) = msg.metadata::json -> 'templating' -> 'template' ->> 'uuid'
                    INNER JOIN public.flows_flow_template_dependencies AS depent
                        ON depent.template_id = template.id
                    INNER JOIN public.flows_flow AS flow
                        ON flow.id = depent.flow_id
                WHERE
                    msg.sent_on BETWEEN '{start_date_str}' AND '{end_date_str}'
                    AND msg.metadata::jsonb -> 'templating' IS NOT NULL
                    AND msg.org_id = {org_id}
                GROUP BY
                    template.name, flow.name
                ORDER BY
                    COUNT(msg.id) DESC;
            """
            cursor.execute(query)
            results = cursor.fetchall()

        return Response(results)
