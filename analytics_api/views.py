from django.db.models import Count, Q, Prefetch
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from temba.contacts.models import Contact, ContactGroup
from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
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

        # filter by UUID (optional)
        uuid = params.get("uuid")
        if uuid:
            queryset = queryset.filter(uuid=uuid)

        # filter by URN (optional)
        urn = params.get("urn")
        if urn:
            queryset = queryset.filter(urns__identity=self.normalize_urn(urn))

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

        return self.filter_before_after(queryset, "modified_on")

    def get(self, request, *args, **kwargs):
        total_and_current_contacts = Contact.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status="A")),
            blocked=Count("id", filter=Q(status="B")),
            stopped=Count("id", filter=Q(status="S")),
            archived=Count("id", filter=Q(status="V"))
        )

        contacts_by_date = Contact.objects.values("created_on__date").annotate(total=Count("created_on__date"))
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
            "by_date": cleaned_contacts_by_date
        }

        return Response(contact_analytics, status=200)
