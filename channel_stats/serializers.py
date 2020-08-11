from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import serializers

from temba.api.v2.serializers import ReadSerializer
from temba.channels.models import Channel, ChannelCount
from temba.contacts.models import Contact
from temba.msgs.models import OUTGOING


class ChannelStatsReadSerializer(ReadSerializer):
    msg_count = serializers.SerializerMethodField()
    ivr_count = serializers.SerializerMethodField()
    error_count = serializers.SerializerMethodField()
    daily_count = serializers.SerializerMethodField()
    monthly_totals = serializers.SerializerMethodField()

    def get_msg_count(self, obj):
        return obj.get_msg_count()

    def get_ivr_count(self, obj):
        return obj.get_ivr_count()

    def get_error_count(self, obj):
        return int(obj.get_error_log_count())

    def get_daily_count(self, obj):
        channel = obj

        end_date = (timezone.now() + timedelta(days=1)).date()
        start_date = end_date - relativedelta(months=12)

        message_stats = []
        channels = [channel]
        for sender in Channel.objects.filter(parent=channel):
            channels.append(sender)

        msg_in = []
        msg_out = []
        ivr_in = []
        ivr_out = []
        error = []

        message_stats.append(dict(name="Incoming", type="msg", data=msg_in))
        message_stats.append(dict(name="Outgoing", type="msg", data=msg_out))
        message_stats.append(dict(name="Errors", type="error", data=error))

        if channel.get_ivr_count():
            message_stats.append(
                dict(name="Incoming", type="ivr", data=ivr_in))
            message_stats.append(
                dict(name="Outgoing", type="ivr", data=ivr_out))
            message_stats.append(dict(name="Errors", type="error", data=error))

        daily_counts = list(
            ChannelCount.objects.filter(
                channel__in=channels, day__gte=start_date)
            .filter(
                count_type__in=[
                    ChannelCount.INCOMING_MSG_TYPE,
                    ChannelCount.OUTGOING_MSG_TYPE,
                    ChannelCount.INCOMING_IVR_TYPE,
                    ChannelCount.OUTGOING_IVR_TYPE,
                    ChannelCount.ERROR_LOG_TYPE,
                ]
            )
            .values("day", "count_type")
            .order_by("day", "count_type")
            .annotate(count_sum=Sum("count"))
        )

        current = start_date
        while current <= end_date:
            while daily_counts and daily_counts[0]["day"] == current:
                daily_count = daily_counts.pop(0)
                if daily_count["count_type"] == ChannelCount.INCOMING_MSG_TYPE:
                    msg_in.append(
                        dict(date=daily_count["day"], count=daily_count["count_sum"]))
                elif daily_count["count_type"] == ChannelCount.OUTGOING_MSG_TYPE:
                    msg_out.append(
                        dict(date=daily_count["day"], count=daily_count["count_sum"]))
                elif daily_count["count_type"] == ChannelCount.INCOMING_IVR_TYPE:
                    ivr_in.append(
                        dict(date=daily_count["day"], count=daily_count["count_sum"]))
                elif daily_count["count_type"] == ChannelCount.OUTGOING_IVR_TYPE:
                    ivr_out.append(
                        dict(date=daily_count["day"], count=daily_count["count_sum"]))
                elif daily_count["count_type"] == ChannelCount.ERROR_LOG_TYPE:
                    error.append(
                        dict(date=daily_count["day"], count=daily_count["count_sum"]))

            current = current + timedelta(days=1)

        return message_stats

    def get_monthly_totals(self, obj):
        channel = obj
        message_stats_table = []
        month_start = channel.created_on.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

        monthly_totals = list(
            ChannelCount.objects.filter(channel=channel, day__gte=month_start)
            .filter(
                count_type__in=[
                    ChannelCount.INCOMING_MSG_TYPE,
                    ChannelCount.OUTGOING_MSG_TYPE,
                    ChannelCount.INCOMING_IVR_TYPE,
                    ChannelCount.OUTGOING_IVR_TYPE,
                    ChannelCount.ERROR_LOG_TYPE,
                ]
            )
            .extra({"month": "date_trunc('month', day)"})
            .values("month", "count_type")
            .order_by("month", "count_type")
            .annotate(count_sum=Sum("count"))
        )

        now = timezone.now()
        while month_start < now:
            msg_in = 0
            msg_out = 0
            ivr_in = 0
            ivr_out = 0
            error = 0

            while monthly_totals and monthly_totals[0]["month"] == month_start:
                monthly_total = monthly_totals.pop(0)
                if monthly_total["count_type"] == ChannelCount.INCOMING_MSG_TYPE:
                    msg_in = monthly_total["count_sum"]
                elif monthly_total["count_type"] == ChannelCount.OUTGOING_MSG_TYPE:
                    msg_out = monthly_total["count_sum"]
                elif monthly_total["count_type"] == ChannelCount.INCOMING_IVR_TYPE:
                    ivr_in = monthly_total["count_sum"]
                elif monthly_total["count_type"] == ChannelCount.OUTGOING_IVR_TYPE:
                    ivr_out = monthly_total["count_sum"]
                elif monthly_total["count_type"] == ChannelCount.ERROR_LOG_TYPE:
                    error = monthly_total["count_sum"]

            message_stats_table.append(
                dict(
                    month_start=month_start,
                    incoming_messages_count=msg_in,
                    outgoing_messages_count=msg_out,
                    incoming_ivr_count=ivr_in,
                    outgoing_ivr_count=ivr_out,
                    error_count=error,
                )
            )

            month_start = (month_start + timedelta(days=32)).replace(day=1)

        message_stats_table.reverse()
        return message_stats_table

    class Meta:
        model = Channel
        fields = (
            "uuid",
            "name",
            "channel_type",
            "msg_count",
            "ivr_count",
            "error_count",
            "daily_count",
            "monthly_totals",
        )


class ContactActiveSerializer(ReadSerializer):
    _msg = None

    sent_on = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    channel_uuid = serializers.SerializerMethodField()
    channel_name = serializers.SerializerMethodField()
    urn = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            "uuid",
            "name",
            "sent_on",
            "message",
            "channel_uuid",
            "channel_name",
            "urn",
        ]

    def msg(self, obj: Contact):
        request = self.context.get("request")
        if not self._msg and request:
            view = self.context.get("view")
            between = (parse_date(request.query_params.get(view.PARAM_START_DATE)),
                       parse_date(request.query_params.get(view.PARAM_END_DATE)))
            self._msg = obj.msgs.select_related("channel", "contact_urn").only(
                "uuid",
                "sent_on",
                "text",
                "contact",
                "channel__uuid",
                "channel__name",
                "contact_urn__identity",
            ).filter(
                direction=OUTGOING,
                sent_on__date__range=between
            ).order_by("-sent_on").first()
        return self._msg

    def get_sent_on(self, obj: Contact):
        msg = self.msg(obj)
        if msg:
            return msg.sent_on

    def get_message(self, obj: Contact):
        msg = self.msg(obj)
        if msg:
            return msg.text

    def get_channel_uuid(self, obj: Contact):
        msg = self.msg(obj)
        if msg:
            return msg.channel.uuid

    def get_channel_name(self, obj: Contact):
        msg = self.msg(obj)
        if msg:
            return msg.channel.name

    def get_urn(self, obj: Contact):
        msg = self.msg(obj)
        if msg:
            return msg.contact_urn.identity
