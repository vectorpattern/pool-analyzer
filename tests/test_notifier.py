import unittest
from unittest.mock import Mock

from src.notifier import (
    send_low_capacity_notification,
    should_send_low_capacity_notification,
)


class NotificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = {
            "timestamp": "2026-09-30T10:00:00+09:00",
            "updated": "09/30 09:58",
            "status": "0～9人程、入場中です",
            "estimated": 5,
            "state": "OPEN",
        }

    def test_notifies_on_transition_to_low_capacity(self) -> None:
        previous_record = {"estimated": 15, "state": "OPEN"}

        self.assertTrue(
            should_send_low_capacity_notification(self.record, previous_record)
        )

    def test_does_not_notify_while_low_capacity_continues(self) -> None:
        previous_record = {"estimated": 5, "state": "OPEN"}

        self.assertFalse(
            should_send_low_capacity_notification(self.record, previous_record)
        )

    def test_does_not_notify_when_closed_or_holiday(self) -> None:
        for state in ("CLOSED", "HOLIDAY"):
            record = {**self.record, "state": state}
            self.assertFalse(should_send_low_capacity_notification(record, None))

    def test_does_not_notify_when_estimated_is_not_five(self) -> None:
        record = {**self.record, "estimated": 15}

        self.assertFalse(should_send_low_capacity_notification(record, None))

    def test_sends_email_through_injected_post_function(self) -> None:
        response = Mock()
        response.json.return_value = {"status": "success"}
        post = Mock(return_value=response)

        send_low_capacity_notification(
            self.record,
            post=post,
            environ={
                "GAS_WEB_APP_URL": "https://script.google.com/macros/s/example/exec",
                "GAS_WEBHOOK_TOKEN": "token",
            },
        )

        post.assert_called_once_with(
            "https://script.google.com/macros/s/example/exec",
            data={
                "token": "token",
                "estimated": "5",
                "updated": "09/30 09:58",
                "timestamp": "2026-09-30T10:00:00+09:00",
                "is_test": "false",
            },
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()

    def test_raises_when_gas_returns_an_error(self) -> None:
        response = Mock()
        response.json.return_value = {"status": "error", "message": "unauthorized"}

        with self.assertRaisesRegex(RuntimeError, "unauthorized"):
            send_low_capacity_notification(
                self.record,
                post=Mock(return_value=response),
                environ={
                    "GAS_WEB_APP_URL": "https://script.google.com/macros/s/example/exec",
                    "GAS_WEBHOOK_TOKEN": "token",
                },
            )


if __name__ == "__main__":
    unittest.main()
