from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class FlagOrgSerializer(serializers.Serializer):
    date_billing_expired = serializers.DateField(
        required=True,
        format=r"%Y-%m-%d",
        input_formats=[
            r"%Y-%m-%d",
        ],
    )
    date_org_will_suspend = serializers.DateField(
        required=True,
        format=r"%Y-%m-%d",
        input_formats=[
            r"%Y-%m-%d",
        ],
    )

    def to_internal_value(self, data):
        return {
            "date_billing_expired": datetime.strptime(data.get("date_billing_expired"), r"%Y-%m-%d").strftime(
                r"%m/%d/%Y"
            ),
            "date_org_will_suspend": datetime.strptime(data.get("date_org_will_suspend"), r"%Y-%m-%d").strftime(
                r"%m/%d/%Y"
            ),
        }
