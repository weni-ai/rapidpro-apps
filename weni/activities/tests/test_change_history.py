from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

from django.test import SimpleTestCase, override_settings

from weni.activities.change_history import notify_change_history
from weni.activities.recent_activities import create_recent_activity
from weni_commons.change_history import Action, Entity, Module


def _build_instance(
    class_name="Flow",
    is_active=True,
    name="Test Flow",
    modified_on=None,
):
    instance = Mock()
    instance.is_active = is_active
    instance.__class__.__name__ = class_name
    instance.name = name
    instance.uuid = uuid4()
    instance.modified_by = Mock(email="user@example.com")
    instance.org = Mock(
        uuid=uuid4(),
        project=Mock(project_uuid=uuid4()),
    )
    instance.modified_on = modified_on or datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
    return instance


class NotifyChangeHistoryTestCase(SimpleTestCase):
    @patch("weni.activities.change_history.Notifier.notify_change")
    def test_create_action(self, notify_change_mock):
        instance = _build_instance(class_name="Flow")

        notify_change_history(instance, created=True)

        notify_change_mock.assert_called_once_with(
            project_uuid=str(instance.org.project.project_uuid),
            user_email="user@example.com",
            date=instance.modified_on,
            action=Action.CREATE,
            entity=Entity.FLOW,
            module=Module.FLOWS,
            object_id=str(instance.uuid),
            object_name="Test Flow",
        )

    @patch("weni.activities.change_history.Notifier.notify_change")
    def test_update_action(self, notify_change_mock):
        instance = _build_instance(class_name="Channel")

        notify_change_history(instance, created=False)

        notify_change_mock.assert_called_once()
        kwargs = notify_change_mock.call_args.kwargs
        self.assertEqual(kwargs["action"], Action.UPDATE)
        self.assertEqual(kwargs["entity"], Entity.CHANNEL)

    @patch("weni.activities.change_history.Notifier.notify_change")
    def test_delete_action(self, notify_change_mock):
        instance = _build_instance(class_name="Flow")

        notify_change_history(instance, created=False, delete=True)

        notify_change_mock.assert_called_once()
        kwargs = notify_change_mock.call_args.kwargs
        self.assertEqual(kwargs["action"], Action.DELETE)
        self.assertEqual(kwargs["entity"], Entity.FLOW)

    @patch("weni.activities.change_history.Notifier.notify_change")
    def test_unknown_entity_is_ignored(self, notify_change_mock):
        instance = _build_instance(class_name="Classifier")

        notify_change_history(instance, created=True)

        notify_change_mock.assert_not_called()


class CreateRecentActivityTestCase(SimpleTestCase):
    @patch("weni.activities.recent_activities.notify_change_history")
    @patch("weni.activities.recent_activities._publish_legacy_recent_activity")
    def test_dual_publish_when_active(
        self,
        publish_legacy_mock,
        notify_change_history_mock,
    ):
        instance = _build_instance()

        create_recent_activity(instance, created=True)

        publish_legacy_mock.assert_called_once_with(instance, True, None)
        notify_change_history_mock.assert_called_once_with(instance, True, delete=False)

    @patch("weni.activities.recent_activities.notify_change_history")
    @patch("weni.activities.recent_activities._publish_legacy_recent_activity")
    def test_inactive_instance_is_ignored(
        self,
        publish_legacy_mock,
        notify_change_history_mock,
    ):
        instance = _build_instance(is_active=False)

        create_recent_activity(instance, created=True)

        publish_legacy_mock.assert_not_called()
        notify_change_history_mock.assert_not_called()

    @override_settings(RECENT_ACTIVITIES_LEGACY_ENABLED=False)
    @patch("weni.activities.recent_activities.notify_change_history")
    @patch("weni.activities.recent_activities._publish_legacy_recent_activity")
    def test_legacy_publish_can_be_disabled(
        self,
        publish_legacy_mock,
        notify_change_history_mock,
    ):
        instance = _build_instance()

        create_recent_activity(instance, created=True)

        publish_legacy_mock.assert_not_called()
        notify_change_history_mock.assert_called_once_with(instance, True, delete=False)

    @override_settings(CHANGE_HISTORY_ENABLED=False)
    @patch("weni.activities.recent_activities.notify_change_history")
    @patch("weni.activities.recent_activities._publish_legacy_recent_activity")
    def test_change_history_can_be_disabled(
        self,
        publish_legacy_mock,
        notify_change_history_mock,
    ):
        instance = _build_instance()

        create_recent_activity(instance, created=True)

        publish_legacy_mock.assert_called_once_with(instance, True, None)
        notify_change_history_mock.assert_not_called()

    @patch("weni.activities.recent_activities.logger")
    @patch("weni.activities.recent_activities.notify_change_history")
    @patch("weni.activities.recent_activities._publish_legacy_recent_activity")
    def test_change_history_failure_does_not_propagate(
        self,
        publish_legacy_mock,
        notify_change_history_mock,
        logger_mock,
    ):
        instance = _build_instance()
        notify_change_history_mock.side_effect = RuntimeError("broker unavailable")

        create_recent_activity(instance, created=True)

        publish_legacy_mock.assert_called_once_with(instance, True, None)
        logger_mock.exception.assert_called_once()

    @patch("weni.activities.recent_activities.notify_change_history")
    @patch("weni.activities.recent_activities._publish_legacy_recent_activity")
    def test_delete_flag_is_forwarded(
        self,
        publish_legacy_mock,
        notify_change_history_mock,
    ):
        instance = _build_instance()

        create_recent_activity(instance, created=False, delete=True)

        publish_legacy_mock.assert_called_once_with(instance, False, True)
        notify_change_history_mock.assert_called_once_with(instance, False, delete=True)
