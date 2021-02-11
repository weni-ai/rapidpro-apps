from rest_framework.reverse import reverse

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.channels.models import Channel

from .serializers import ChannelStatsReadSerializer


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
