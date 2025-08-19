from temba.channels.models import Channel
from temba.event_driven.publisher.rabbitmq_publisher import RabbitmqPublisher


def publish_channel_event(channel: Channel, action: str):
    
    rabbitmq_publisher = RabbitmqPublisher()
    
    rabbitmq_publisher.send_message(
        body=dict(
            action=action,
            uuid=channel.uuid,
            project_uuid=str(channel.org.proj_uuid),
            channel_type=channel.channel_type,
            waba=channel.config.get("wa_waba_id", None) if channel.channel_type == "WAC" else None,
            phone_number=channel.config.get("wa_number", None) if channel.channel_type == "WAC" else None,
            is_demo=channel.config.get("is_demo", False),
        ),
        exchange="channel-events.topic",
        routing_key="",
    )
