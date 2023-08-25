# TODO: move code to a package and separate between logic and exceptions

from typing import TYPE_CHECKING

from django.db.models import Exists, OuterRef, Case, When, Value, BooleanField, F
from django.contrib.auth import get_user_model

from temba.orgs.models import Org
from temba.classifiers.models import Classifier
from temba.flows.models import Flow
from temba.channels.models import Channel
from temba.msgs.models import Msg


if TYPE_CHECKING:
    from django.db.models.query import QuerySet


User = get_user_model()


SUCCESS_ORG_QUERIES = dict(
    has_ia=Exists(
        Classifier.objects.filter(
            org=OuterRef("pk"), classifier_type="bothub", is_active=True
        )
    ),
    has_flows=Exists(Flow.objects.filter(org=OuterRef("pk"), is_active=True)),
    has_channel=Exists(Channel.objects.filter(org=OuterRef("pk"), is_active=True)),
    has_msg=Exists(Msg.objects.filter(org=OuterRef("pk"))),
    has_channel_production=Exists(
        Channel.objects.filter(org=OuterRef("pk"), is_active=True).exclude(
            name="WhatsApp: +558231420933"
        )
    ),
)


class UserDoesNotExist(User.DoesNotExist):
    pass


class OrgDoesNotExist(Org.DoesNotExist):
    pass


def user_has_org_permission(user: User, org: Org) -> bool:
    return (
        org.created_by == user
        or user.org_admins.filter(pk=org.pk)
        or user.org_viewers.filter(pk=org.pk)
        or user.org_editors.filter(pk=org.pk)
        or user.org_surveyors.filter(pk=org.pk)
    )


def get_user_by_email(email: str) -> User:
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist as error:
        raise UserDoesNotExist(error)


def get_success_orgs() -> "QuerySet[Org]":
    return (
        Org.objects.annotate(user_last_login=F("created_by__last_login"))
        .annotate(**SUCCESS_ORG_QUERIES)
        .annotate(
            is_success_project=Case(
                When(
                    has_ia=True,
                    has_flows=True,
                    has_channel=True,
                    has_msg=True,
                    has_channel_production=True,
                    then=Value(True),
                ),
                output_field=BooleanField(),
                default=Value(False),
            )
        )
    )


def get_user_success_orgs(user: User) -> "QuerySet[Org]":
    return get_success_orgs().filter(created_by=user)


def get_user_success_orgs_by_email(email: str) -> dict:
    user = get_user_by_email(email)

    return dict(
        email=user.email, last_login=user.last_login, orgs=get_user_success_orgs(user)
    )


def retrieve_success_org(org_uuid: str) -> Org:
    try:
        return get_success_orgs().get(uuid=org_uuid)
    except Org.DoesNotExist as error:
        raise OrgDoesNotExist(error)
