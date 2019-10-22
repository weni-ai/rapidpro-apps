from rest_framework.reverse import reverse

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin

from temba.channels.models import Channel
from .serializers import ChannelStatsReadSerializer


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
            "url": reverse("api.v2.channels_stats"),
            "slug": "channel-stats",
            "params": [
                {
                    "name": "uuid",
                    "required": True,
                    "help": "A channel UUID to filter by. ex: 09d23a05-47fe-11e4-bfe9-b8f6b119e9ab",
                }
            ],
        }
