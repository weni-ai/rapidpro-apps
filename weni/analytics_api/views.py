from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from rest_framework.response import Response

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.contacts.models import Contact, ContactGroup
from temba.flows.models import FlowRun
from temba.utils import str_to_bool


class ContactAnalyticsEndpoint(BaseAPIView, ListAPIMixin):
    """
    This endpoint shows the analytical data of the contacts over a period of time.

    ## List Analytics Contacts data

    A **GET** returns analytical data related to contacts, containing segmentation by time and by type.

    * **group** - A group name or UUID to filter by. ex: Customers.
    * **deleted** - Whether to return only deleted contacts. ex: false.
    * **before** - Only return events created before this date, ex: 2015-01-28T18:00:00.000
    * **after** - Only return events created after this date, ex: 2015-01-28T18:00:00.000

    Example:

        GET /api/v2/analytics/contacts

    Response:
        {
            "total": 100,
            "current": {
                "actives": 100,
                "blocked": 0,
                "stopped": 0,
                "archived": 0
            },
            "by_date": {
                "2019-02-07": 10,
                "2020-12-23": 30,
                "2018-11-01": 60,
            }
        }
    """

    permission = "contacts.contact_api"
    model = Contact
    lookup_params = {"uuid": "uuid", "urn": "urns__identity"}

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

    @classmethod
    def get_read_explorer(cls):
        return {
            "method": "GET",
            "title": "List Contacts Analytics",
            "url": reverse("api.v2.analytics.contacts"),
            "slug": "contacts-analytics",
            "params": [
                {
                    "name": "group",
                    "required": False,
                    "help": "A group name or UUID to filter by. ex: Customers",
                },
                {
                    "name": "deleted",
                    "required": False,
                    "help": "Whether to return only deleted contacts. ex: false",
                },
                {
                    "name": "before",
                    "required": False,
                    "help": "Only return events created before this date, ex: 2015-01-28T18:00:00.000",
                },
                {
                    "name": "after",
                    "required": False,
                    "help": "Only return events created after this date, ex: 2015-01-28T18:00:00.000",
                },
            ],
        }


# This endpoint has been deactivate in March, 2024
class FlowRunAnalyticsEndpoint(BaseAPIView, ListAPIMixin):
    """
    This endpoint shows the analytical data of the flow runs over a period of time.

    ## List Analytics Flow Runs data

    A **GET** returns analytical data related to flows, containing information about the type
                of runs and being able to segment by date

    * **flow_uuid** - A flow UUID to filter by, ex: f5901b62-ba76-4003-9c62-72fdacc1b7b7.
    * **before** - Only return events created before this date, ex: 2015-01-28T18:00:00.000
    * **after** - Only return events created after this date, ex: 2015-01-28T18:00:00.000

    Example:

        GET /api/v2/analytics/flow-runs

    Response:
        {
            "Full Call Flow": {
                "uuid": "f5901b62-ba76-4003-9c62-72fdacc1b7b7",
                "stats": {
                    "total": 7,
                    "by_status": {
                        "active": 0,
                        "waiting": 0,
                        "completed": 4,
                        "interrupted": 3,
                        "expired": 0,
                        "failed": 0
                    }
                }
            }
        }
    """

    permission = "flows.flow_api"
    model = FlowRun

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

    @classmethod
    def get_read_explorer(cls):
        return {
            "method": "GET",
            "title": "List Flow Runs Analytics",
            "url": reverse("api.v2.analytics.flow_runs"),
            "slug": "flow-runs-analytics",
            "params": [
                {
                    "name": "flow_uuid",
                    "required": False,
                    "help": "A flow UUID to filter by, ex: f5901b62-ba76-4003-9c62-72fdacc1b7b7",
                },
                {
                    "name": "before",
                    "required": False,
                    "help": "Only return events created before this date, ex: 2015-01-28T18:00:00.000",
                },
                {
                    "name": "after",
                    "required": False,
                    "help": "Only return events created after this date, ex: 2015-01-28T18:00:00.000",
                },
            ],
        }
