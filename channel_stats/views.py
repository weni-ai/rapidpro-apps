from django.db.models import Prefetch, Exists, OuterRef
from django.utils.dateparse import parse_date
from rest_framework.reverse import reverse

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.channels.models import Channel
from temba.contacts.models import Contact
from temba.msgs.models import Msg, OUTGOING
from temba.orgs.models import Org
from .serializers import ContactActiveSerializer, ChannelStatsReadSerializer


class ChannelStatsEndpoint(ListAPIMixin, BaseAPIView):
    permission = "channels.channel_api"
    model = Channel
    serializer_class = ChannelStatsReadSerializer

    def filter_queryset(self, queryset):
        params = self.request.query_params
        queryset = queryset.filter(is_active=True)

        uuid = params.get("uuid")
        if uuid:
            queryset = queryset.filter(uuid=uuid)

        return queryset

    @classmethod
    def get_read_explorer(cls):
        return {
            "method": "GET",
            "title": "List Channel Stats",
            "url": reverse("api.v2.channel_stats.channels"),
            "slug": "channel-stats",
            "params": [
                {
                    "name": "uuid",
                    "required": True,
                    "help": "A channel UUID to filter by. ex: 09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                }
            ],
        }


class ContactsActiveEndpoint(ListAPIMixin, BaseAPIView):
    PARAM_ORG_ID = "org_id"
    PARAM_START_DATE = "start_date"
    PARAM_END_DATE = "end_date"

    permission = "contacts.contact_api"
    model = Contact
    serializer_class = ContactActiveSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            org = Org.objects.filter(pk=self.request.query_params.get(self.PARAM_ORG_ID))
        else:
            org = self.request.user.get_org()

        between = (parse_date(self.request.query_params.get(self.PARAM_START_DATE)),
                   parse_date(self.request.query_params.get(self.PARAM_END_DATE)))
        return super().get_queryset().prefetch_related(Prefetch(
            "msgs", Msg.objects.select_related("channel").only(
                "uuid",
                "sent_on",
                "text",
                "contact",
                "channel__uuid",
                "channel__name",
            ).filter(pk__in=Msg.objects.order_by("-sent_on").values("pk")[:1])
        )).annotate(
            has_msg=Exists(Msg.objects.filter(
                contact__pk=OuterRef("pk"), direction=OUTGOING, sent_on__date__range=between
            ).values("pk"))
        ).only("uuid", "name").filter(org=org, has_msg=True)

    @classmethod
    def get_read_explorer(cls):
        return {
            "method": "GET",
            "title": "List Channel Stats",
            "url": reverse("api.v2.channels_stats"),
            "slug": "channel-stats",
            "params": [
                {
                    "name": cls.PARAM_ORG_ID,
                    "required": False,
                    "help": "Integer ID. This field is required if the user is a super user.",
                },
                {
                    "name": cls.PARAM_START_DATE,
                    "required": True,
                    "help": "Start date in format YYYY-MM-DD",
                },
                {
                    "name": cls.PARAM_END_DATE,
                    "required": True,
                    "help": "End date in format YYYY-MM-DD",
                },
            ],
        }
