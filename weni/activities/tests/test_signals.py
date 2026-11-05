from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from weni_commons.change_history import Action

from weni.activities.change_history import PREVIOUS_NAME_ATTR
from weni.activities.signals import (
    ARCHIVE_UPDATE_FIELDS,
    FLOW_REVISION_UPDATE_FIELDS,
    channel_recent_activity_signal,
    flow_recent_activity_signal,
    remember_previous_name,
    trigger_recent_activity_signal,
)

RELEASE_UPDATE_FIELDS = frozenset({"is_active", "modified_by", "modified_on"})


def _build_flow(has_revisions=True, is_active=True, is_archived=False, is_system=False):
    flow = Mock()
    flow.is_active = is_active
    flow.is_archived = is_archived
    flow.is_system = is_system
    flow.revisions.exists.return_value = has_revisions
    return flow


@patch("weni.activities.signals.create_change_history_activity")
@patch("weni.activities.signals.create_recent_activity")
class FlowRecentActivitySignalTestCase(SimpleTestCase):
    def test_regular_save_publishes_recent_activity(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow()

        flow_recent_activity_signal(sender=None, instance=flow, created=True, update_fields=None)

        create_recent_activity_mock.assert_called_once_with(flow, True)
        change_history_mock.assert_not_called()

    def test_editor_save_publishes_change_history_only(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow(has_revisions=True)

        flow_recent_activity_signal(
            sender=None, instance=flow, created=False, update_fields=FLOW_REVISION_UPDATE_FIELDS
        )

        create_recent_activity_mock.assert_not_called()
        change_history_mock.assert_called_once_with(flow, created=False)

    def test_first_revision_is_ignored(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow(has_revisions=False)

        flow_recent_activity_signal(
            sender=None, instance=flow, created=False, update_fields=FLOW_REVISION_UPDATE_FIELDS
        )

        create_recent_activity_mock.assert_not_called()
        change_history_mock.assert_not_called()

    def test_flow_release_publishes_change_history_delete(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow(is_active=False)

        flow_recent_activity_signal(sender=None, instance=flow, created=False, update_fields=RELEASE_UPDATE_FIELDS)

        change_history_mock.assert_called_once_with(flow, created=False, delete=True)
        create_recent_activity_mock.assert_not_called()

    def test_system_flow_release_is_ignored(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow(is_active=False, is_system=True)

        flow_recent_activity_signal(sender=None, instance=flow, created=False, update_fields=RELEASE_UPDATE_FIELDS)

        change_history_mock.assert_not_called()
        create_recent_activity_mock.assert_not_called()

    def test_flow_archive_publishes_deactivate(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow(is_archived=True)

        flow_recent_activity_signal(sender=None, instance=flow, created=False, update_fields=ARCHIVE_UPDATE_FIELDS)

        create_recent_activity_mock.assert_called_once_with(flow, False, change_history_action=Action.DEACTIVATE)
        change_history_mock.assert_not_called()

    def test_flow_restore_publishes_activate(self, create_recent_activity_mock, change_history_mock):
        flow = _build_flow(is_archived=False)

        flow_recent_activity_signal(sender=None, instance=flow, created=False, update_fields=ARCHIVE_UPDATE_FIELDS)

        create_recent_activity_mock.assert_called_once_with(flow, False, change_history_action=Action.ACTIVATE)
        change_history_mock.assert_not_called()


@patch("weni.activities.signals.create_change_history_activity")
@patch("weni.activities.signals.create_recent_activity")
class ChannelRecentActivitySignalTestCase(SimpleTestCase):
    def test_channel_release_publishes_change_history_delete(self, create_recent_activity_mock, change_history_mock):
        channel = Mock(is_active=False, channel_type="WAC")

        channel_recent_activity_signal(
            sender=None,
            instance=channel,
            created=False,
            update_fields=frozenset({"is_active", "config", "modified_by", "modified_on"}),
        )

        change_history_mock.assert_called_once_with(channel, created=False, delete=True)
        create_recent_activity_mock.assert_not_called()

    def test_whatsapp_config_save_is_ignored(self, create_recent_activity_mock, change_history_mock):
        channel = Mock(is_active=True, channel_type="WAC")

        channel_recent_activity_signal(
            sender=None, instance=channel, created=False, update_fields=frozenset({"config"})
        )

        create_recent_activity_mock.assert_not_called()
        change_history_mock.assert_not_called()

    def test_regular_save_publishes_recent_activity(self, create_recent_activity_mock, change_history_mock):
        channel = Mock(is_active=True, channel_type="TG")

        channel_recent_activity_signal(sender=None, instance=channel, created=False, update_fields=None)

        create_recent_activity_mock.assert_called_once_with(channel, False)
        change_history_mock.assert_not_called()


@patch("weni.activities.signals.create_change_history_activity")
@patch("weni.activities.signals.create_recent_activity")
class TriggerRecentActivitySignalTestCase(SimpleTestCase):
    def test_trigger_release_publishes_change_history_delete(self, create_recent_activity_mock, change_history_mock):
        trigger = Mock(is_active=False)

        trigger_recent_activity_signal(
            sender=None, instance=trigger, created=False, update_fields=RELEASE_UPDATE_FIELDS
        )

        change_history_mock.assert_called_once_with(trigger, created=False, delete=True)
        create_recent_activity_mock.assert_not_called()

    def test_trigger_archive_publishes_deactivate(self, create_recent_activity_mock, change_history_mock):
        trigger = Mock(is_active=True, is_archived=True)

        trigger_recent_activity_signal(
            sender=None, instance=trigger, created=False, update_fields=ARCHIVE_UPDATE_FIELDS
        )

        create_recent_activity_mock.assert_called_once_with(
            trigger, False, change_history_action=Action.DEACTIVATE
        )
        change_history_mock.assert_not_called()

    def test_trigger_restore_publishes_activate(self, create_recent_activity_mock, change_history_mock):
        trigger = Mock(is_active=True, is_archived=False)

        trigger_recent_activity_signal(
            sender=None, instance=trigger, created=False, update_fields=ARCHIVE_UPDATE_FIELDS
        )

        create_recent_activity_mock.assert_called_once_with(
            trigger, False, change_history_action=Action.ACTIVATE
        )
        change_history_mock.assert_not_called()

    def test_regular_save_publishes_recent_activity(self, create_recent_activity_mock, change_history_mock):
        trigger = Mock(is_active=True)

        trigger_recent_activity_signal(sender=None, instance=trigger, created=True, update_fields=None)

        create_recent_activity_mock.assert_called_once_with(trigger, True)
        change_history_mock.assert_not_called()


def _build_saved_instance(is_system=False):
    instance = Mock(pk=1, is_system=is_system)
    instance._state.adding = False
    return instance


def _build_sender(previous_name="A"):
    sender = Mock()
    sender._base_manager.filter.return_value.values_list.return_value.first.return_value = previous_name
    return sender


class RememberPreviousNameTestCase(SimpleTestCase):
    def test_pre_save_remembers_previous_name(self):
        sender = _build_sender(previous_name="A")
        instance = _build_saved_instance()

        remember_previous_name(sender=sender, instance=instance, update_fields=None)

        sender._base_manager.filter.assert_called_once_with(pk=1)
        self.assertEqual(instance.__dict__[PREVIOUS_NAME_ATTR], "A")

    def test_pre_save_queries_when_name_in_update_fields(self):
        sender = _build_sender(previous_name="A")
        instance = _build_saved_instance()

        remember_previous_name(
            sender=sender, instance=instance, update_fields=frozenset({"name", "expires_after_minutes"})
        )

        self.assertEqual(instance.__dict__[PREVIOUS_NAME_ATTR], "A")

    def test_pre_save_skips_query_when_name_not_in_update_fields(self):
        sender = _build_sender()
        instance = _build_saved_instance()
        instance.__dict__[PREVIOUS_NAME_ATTR] = "stale"

        remember_previous_name(sender=sender, instance=instance, update_fields=FLOW_REVISION_UPDATE_FIELDS)

        sender._base_manager.filter.assert_not_called()
        self.assertNotIn(PREVIOUS_NAME_ATTR, instance.__dict__)

    def test_pre_save_skips_new_instances(self):
        sender = _build_sender()
        instance = _build_saved_instance()
        instance._state.adding = True

        remember_previous_name(sender=sender, instance=instance, update_fields=None)

        sender._base_manager.filter.assert_not_called()
        self.assertNotIn(PREVIOUS_NAME_ATTR, instance.__dict__)

    def test_pre_save_skips_system_flows(self):
        sender = _build_sender()
        instance = _build_saved_instance(is_system=True)

        remember_previous_name(sender=sender, instance=instance, update_fields=None)

        sender._base_manager.filter.assert_not_called()
        self.assertNotIn(PREVIOUS_NAME_ATTR, instance.__dict__)
