from django.db.models import Exists, OuterRef
from django.http import Http404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.channels.models import Channel
from temba.contacts.models import Contact
from temba.msgs.models import Msg, OUTGOING
from temba.orgs.models import Org
from .serializers import ContactActiveSerializer, ChannelStatsReadSerializer


class ChannelStatsEndpoint(ListAPIMixin, BaseAPIView):
    """
    This endpoint shows the statistics of messages sent and received by channel.

    ## List Statistics of Messages by Channels

    A **GET** returns the list of the channels of the statistic of messages sent and received for your organization.

    * **uuid** - UUID of the channel.

    Example:

        GET /api/v2/channel_stats.json

    Response:

        {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                {
                    "uuid": "600c1831-7f6a-44a3-b1db-78567500553f",
                    "name": "Web",
                    "channel_type": "EX",
                    "msg_count": 1605,
                    "ivr_count": 0,
                    "error_count": 0,
                    "daily_count": [
                        {
                            "name": "Incoming",
                            "type": "msg",
                            "data": [
                                {
                                "date": "2020-01-01",
                                "count": 3
                                }
                            ]
                        },
                        {
                            "name": "Outgoing",
                            "type": "msg",
                            "data": [
                                {
                                "date": "2020-01-01",
                                "count": 3
                                }
                            ]
                        },
                        {
                            "name": "Errors",
                            "type": "error",
                            "data": [
                                {
                                "date": "2020-01-01",
                                "count": 3
                                }
                            ]
                        }
                    ],
                    "monthly_totals": [
                        {
                            "month_start": "2020-01-01T00:00:00Z",
                            "incoming_messages_count": 73,
                            "outgoing_messages_count": 106,
                            "incoming_ivr_count": 0,
                            "outgoing_ivr_count": 0,
                            "error_count": 0
                        }
                    ]
                }
            ]
        }
    """
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


class ActiveContactsEndpoint(ListAPIMixin, BaseAPIView):
    """
    This endpoint allow you to list all contacts that received messages in a period based on current date.

    ## Listing Active Contacts

    A **GET** returns the list of the active contacts for your organization or to the selected organization if is a
    super user.

    * **org_id** - org ID (integer). This field is **required** if the user is a superuser;
    * **start_date** - Start range date in ISO format (date - YYYY-MM-DD). The minimum value is the first day of the
      last month;
    * **end_date** - End range date in ISO format (date - YYYY-MM-DD).

    Example:

        GET /api/v2/channel_stats/contacts.json

    Response:

        {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                {
                    "uuid": "e942cc37-fe71-45df-b445-2b7b51461eb6"
                    "name": "Contact Name"
                    "sent_on": "2020-10-01T00:00:00+00:00"
                    "message": "Last message sent"
                    "channel_uuid": "e0ff422a-5b58-4a83-956b-920e2033e5f3"
                    "channel_name": "Channel name"
                }
            ]
        }

    ### Important:

    The **404 status** will happen if the organization's ID cannot be found.
    """
    DAYS_RANGE = 31
    PARAM_ORG_ID = "org_id"
    PARAM_START_DATE = "start_date"
    PARAM_END_DATE = "end_date"

    permission = "contacts.contact_api"
    model = Contact
    serializer_class = ContactActiveSerializer

    def filter_queryset(self, queryset):
        if self.request.user.is_superuser:
            org = Org.objects.filter(pk=self.request.query_params.get(self.PARAM_ORG_ID)).first()
        else:
            org = self.request.user.get_org()

        if not org:
            raise Http404

        between = (parse_date(self.request.query_params.get(self.PARAM_START_DATE)),
                   parse_date(self.request.query_params.get(self.PARAM_END_DATE)))
        return queryset.annotate(
            has_msg=Exists(Msg.objects.filter(
                contact__pk=OuterRef("pk"), direction=OUTGOING, sent_on__date__range=between,
            ).values("pk"))
        ).only("uuid", "name").filter(org=org, has_msg=True)

    @classmethod
    def get_read_explorer(cls):
        return {
            "method": "GET",
            "title": "List Channel Stats",
            "url": reverse("api.v2.channel_stats.contacts"),
            "slug": "channel-stats-active-contacts",
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

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser and not self.request.query_params.get(self.PARAM_ORG_ID):
            return Response(
                {self.PARAM_ORG_ID: "Superuser must inform a value"},
                status=HTTP_400_BAD_REQUEST
            )

        start_date = parse_date(self.request.query_params.get(self.PARAM_START_DATE) or "")
        end_date = parse_date(self.request.query_params.get(self.PARAM_END_DATE) or "")
        if not start_date:
            return Response({self.PARAM_START_DATE: "Required parameter."})
        elif not end_date:
            return Response({self.PARAM_END_DATE: "Required parameter."})
        elif end_date <= start_date:
            return Response({self.PARAM_END_DATE: f"Field must be greater then \"{self.PARAM_START_DATE}\""})
        elif start_date.month < timezone.now().month - 1:
            return Response({self.PARAM_START_DATE: f""})
        elif (end_date - start_date).days > self.DAYS_RANGE:
            return Response({"detail": f"The range can not me greater then {self.DAYS_RANGE} days"})
        return super().get(request, *args, **kwargs)
