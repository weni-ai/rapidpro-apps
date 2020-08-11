from django.utils.dateparse import parse_date
from rest_framework import serializers

from temba.api.v2.serializers import ReadSerializer
from temba.contacts.models import Contact
from temba.msgs.models import OUTGOING


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
