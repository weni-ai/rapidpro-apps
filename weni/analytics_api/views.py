from django.db.models import Count, Prefetch, Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.contacts.models import Contact, ContactGroup
from temba.flows.models import FlowRun
from temba.utils import str_to_bool


class ContactAnalyticsEndpoint(BaseAPIView, ListAPIMixin):
    permission = "contacts.contact_api"
    model = Contact
    lookup_params = {"uuid": "uuid", "urn": "urns__identity"}
    renderer_classes = [JSONRenderer]

    def filter_queryset(self, queryset):
        params = self.request.query_params
        org = self.request.user.get_org()

        deleted_only = str_to_bool(params.get("deleted"))
        queryset = queryset.filter(is_active=(not deleted_only))

        # filter by group name/uuid (optional)
        group_ref = params.get("group")
        if group_ref:
            group = ContactGroup.user_groups.filter(org=org).filter(Q(uuid=group_ref) | Q(name=group_ref)).first()
            if group:
                queryset = queryset.filter(all_groups=group)
            else:
                queryset = queryset.filter(pk=-1)

        # use prefetch rather than select_related for foreign keys to avoid joins
        queryset = queryset.prefetch_related(
            Prefetch(
                "all_groups",
                queryset=ContactGroup.user_groups.only("uuid", "name").order_by("pk"),
                to_attr="prefetched_user_groups",
            )
        )

        return self.filter_before_after(queryset, "created_on")

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        total_and_current_contacts = queryset.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status="A")),
            blocked=Count("id", filter=Q(status="B")),
            stopped=Count("id", filter=Q(status="S")),
            archived=Count("id", filter=Q(status="V")),
        )

        contacts_by_date = queryset.values("created_on__date").annotate(total=Count("created_on__date"))
        cleaned_contacts_by_date = {}

        for date in contacts_by_date:
            cleaned_contacts_by_date[date.get("created_on__date").strftime("%Y-%m-%d")] = date.get("total")

        contact_analytics = {
            "total": total_and_current_contacts.get("total"),
            "current": {
                "actives": total_and_current_contacts.get("active"),
                "blocked": total_and_current_contacts.get("blocked"),
                "stopped": total_and_current_contacts.get("stopped"),
                "archived": total_and_current_contacts.get("archived"),
            },
            "by_date": cleaned_contacts_by_date,
        }

        return Response(contact_analytics, status=200)


class FlowRunAnalyticsEndpoint(BaseAPIView, ListAPIMixin):
    permission = "flows.flow_api"
    model = FlowRun
    renderer_classes = [JSONRenderer]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        params = self.request.query_params

        flow_uuid = params.get("flow_uuid")
        if flow_uuid:
            queryset = queryset.filter(flow__uuid=flow_uuid)

        return self.filter_before_after(queryset, "created_on")

    def get(self, request, *args, **kwargs):
        flows_runs = self.filter_queryset(self.get_queryset())
        flows_runs_stats = flows_runs.values("flow__uuid", "flow__name").annotate(
            total=Count("id"),
            status_active=Count("id", filter=Q(status=FlowRun.STATUS_ACTIVE)),
            status_waiting=Count("id", filter=Q(status=FlowRun.STATUS_WAITING)),
            status_completed=Count("id", filter=Q(status=FlowRun.STATUS_COMPLETED)),
            status_interrupted=Count("id", filter=Q(status=FlowRun.STATUS_INTERRUPTED)),
            status_expired=Count("id", filter=Q(status=FlowRun.STATUS_EXPIRED)),
            status_failed=Count("id", filter=Q(status=FlowRun.STATUS_FAILED)),
        )

        flows_runs_stats_cleaned = {
            flow_run_stats.get("flow__name"): {
                "uuid": flow_run_stats.get("flow__uuid"),
                "stats": {
                    "total": flow_run_stats.get("total"),
                    "by_status": {
                        "active": flow_run_stats.get("status_active"),
                        "waiting": flow_run_stats.get("status_waiting"),
                        "completed": flow_run_stats.get("status_completed"),
                        "interrupted": flow_run_stats.get("status_interrupted"),
                        "expired": flow_run_stats.get("status_expired"),
                        "failed": flow_run_stats.get("status_failed"),
                    },
                },
            }
            for flow_run_stats in flows_runs_stats
        }
        return Response(flows_runs_stats_cleaned, status=200)
