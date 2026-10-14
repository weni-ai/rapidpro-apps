from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from weni.activities.signals import FLOW_REVISION_UPDATE_FIELDS, flow_recent_activity_signal


def _build_flow(has_revisions=True):
    flow = Mock()
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
