import requests

from django.utils import timezone

from temba.request_logs.models import HTTPLog

from ...models import ClassifierType, Intent
from .views import ConnectView


class BotHubType(ClassifierType):
    """
    Type for classifiers from Bothub
    """

    CONFIG_ACCESS_TOKEN = "access_token"

    name = "BotHub"
    slug = "bothub"
    icon = "icon-bothub"

    connect_view = ConnectView
    connect_blurb = """
        <a href="https://bothub.it">Bothub</a> is an Open Source NLP platform. It supports 29 languages ​​and is evolving to include the languages ​​and dialects of remote cultures.
        """

    form_blurb = """
        You can find the access token for your bot on the Integration tab.
        """

    INTENT_URL = "https://nlp.bothub.it/info/"

    def get_active_intents_from_api(self, classifier, logs):
        access_token = classifier.config[self.CONFIG_ACCESS_TOKEN]

        start = timezone.now()
        try:
            response = requests.get(self.INTENT_URL, headers={"Authorization": f"Bearer {access_token}"})
            elapsed = (timezone.now() - start).total_seconds() * 1000

            log = HTTPLog.from_response(HTTPLog.INTENTS_SYNCED, self.INTENT_URL, response, classifier=classifier)
            log.request_time = elapsed
            logs.append(log)

            response.raise_for_status()
            response_json = response.json()
        except requests.RequestException as e:
            log = HTTPLog.from_exception(HTTPLog.INTENTS_SYNCED, self.INTENT_URL, e, start, classifier=classifier)
            logs.append(log)
            return []

        intents = []
        for intent in response_json["intents"]:
            intents.append(Intent(name=intent, external_id=intent))

        return intents
