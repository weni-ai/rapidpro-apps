from django.db.models import Exists, OuterRef, Case, When, Value, BooleanField, F
from django.contrib.auth import get_user_model

from temba.orgs.models import Org
from temba.classifiers.models import Classifier
from temba.flows.models import Flow
from temba.channels.models import Channel
from temba.msgs.models import Msg


User = get_user_model()


SUCCESS_ORG_QUERIES = dict(
    has_ia=Exists(Classifier.objects.filter(org=OuterRef("pk"), classifier_type="bothub", is_active=True)),
    has_flows=Exists(Flow.objects.filter(org=OuterRef("pk"), is_active=True)),
    has_channel=Exists(Channel.objects.filter(org=OuterRef("pk"), is_active=True)),
    has_msg=Exists(Msg.objects.filter(org=OuterRef("pk"))),
)


class UserDoesNotExist(User.DoesNotExist):
    pass


def get_user_by_email(email: str) -> User:
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist as error:
        raise UserDoesNotExist(error)


def get_user_orgs(user: User):
    return Org.objects.filter(created_by=user)


def get_user_success_orgs(user: User):
    user_orgs = get_user_orgs(user)

    return (
        user_orgs.annotate(user_last_login=F("created_by__last_login"))
        .annotate(**SUCCESS_ORG_QUERIES)
        .annotate(
            is_success_project=Case(
                When(has_ia=True, has_flows=True, has_channel=True, has_msg=True, then=Value(True)),
                output_field=BooleanField(),
                default=Value(False),
            )
        )
    )


def get_user_success_orgs_by_email(email: str):
    user = get_user_by_email(email)

    return dict(email=user.email, last_login=user.last_login, orgs=get_user_success_orgs(user))
