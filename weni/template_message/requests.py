import requests

from django.conf import settings


class TemplateMessageRequest(object):

    def list_template_messages(self, waba_id: str) -> dict:
        params = dict(
            access_token=settings.WHATSAPP_SYSTEM_USER_ACCESS_TOKEN
        )

        response = requests.get(url=f"https://graph.facebook.com/v14.0/{waba_id}/message_templates", params=params)

        return response.json()

    def get_template_namespace(self, waba_id: str) -> dict:
        params = dict(
            fields="message_template_namespace",
            access_token=settings.WHATSAPP_SYSTEM_USER_ACCESS_TOKEN,
        )

        response = requests.get(url=f"https://graph.facebook.com/v14.0/{waba_id}", params=params)

        return response.json().get("message_template_namespace")
