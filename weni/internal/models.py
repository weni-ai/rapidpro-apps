from abc import ABCMeta
from collections import OrderedDict

from django.db import models
from smartmin.models import SmartModel
from django.template import Engine
from django.conf.urls import url

from temba.tickets.models import Ticketer, Topic
from temba.orgs.models import DependencyMixin, Org
from temba.utils.uuid import uuid4



class TicketerQueue(Topic):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, parent_link=True, related_name="queue")
    ticketer = models.ForeignKey(Ticketer, on_delete=models.CASCADE, related_name="queues")

    class Meta:
        db_table = "internal_tickets_ticketerqueue"

    def __str__(self):
        return f"Queue[uuid={self.uuid}, name={self.name}]"

class ExternalServiceType(metaclass=ABCMeta):
    """
    ExternalServiceType is our abstraction base type for external services.
    """
    name = None
    slug = None
    connect_blurb = None
    connect_view = None

    def is_available_to(self, user):
        return True
    
    def get_connected_blurb(self):
        return Engine.get_default().from_string(str(self.connect_blurb))

    def get_urls(self):
        return [self.get_connect_url()]

    def get_connect_url(self):
        return url(r"^connect", self.connect_view.as_view(external_service_type=self), name="connect")

class ExternalService(SmartModel, DependencyMixin):
    """
    A external service that can perform actions 
    """
    uuid = models.UUIDField(default=uuid4)
    external_service_type = models.Charfield(max_length=16)
    org = models.ForeignKey(Org, on_delete=models.PROTECT, related_name="external_services")
    name = models.CharField(max_length=64)
    config = models.JSONField()

    @classmethod
    def create(cls, org, user, external_service_type: str, name: str, config: dict):
        return cls.objects.create(
            uuid=uuid4(),
            external_service_type=external_service_type,
            name=name,
            config=config,
            org=org,
            created_by=user,
            modified_by=user,
        )
    
    @classmethod
    def get_types(cls):
        """
        Returns the possible types available for external services
        """
        types = OrderedDict({})

    def __str__(self):
        return f"ExternalService[uuid={self.uuid}, name={self.name}"
