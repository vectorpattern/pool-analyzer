import unittest

from src.notifier import (
    send_low_capacity_notification,
    should_send_low_capacity_notification,
)


class FakeSMTP:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.started_tls = False
        self.credentials = None
        self.message = None
        self.closed = False

    def starttls(self) -> None:
        self.started_tls = True

    def login(self, username: str, password: str) -> None:
        self.credentials = (username, password)

    def send_message(self, message) -> None:
        self.message = message

    def quit(self) -> None:
        self.closed = True


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

    def test_sends_email_through_injected_smtp_factory(self) -> None:
        smtp_instances = []

        def smtp_factory(host: str, port: int) -> FakeSMTP:
            smtp = FakeSMTP(host, port)
            smtp_instances.append(smtp)
            return smtp

        send_low_capacity_notification(
            self.record,
            smtp_factory=smtp_factory,
            environ={
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "user",
                "SMTP_PASSWORD": "password",
                "MAIL_FROM": "from@example.com",
                "MAIL_TO": "to@example.com",
            },
        )

        smtp = smtp_instances[0]
        self.assertEqual(smtp.host, "smtp.example.com")
        self.assertEqual(smtp.port, 587)
        self.assertTrue(smtp.started_tls)
        self.assertEqual(smtp.credentials, ("user", "password"))
        self.assertTrue(smtp.closed)
        self.assertEqual(smtp.message["Subject"], "四街道市温水プール：低混雑のお知らせ")
        self.assertIn("四街道市温水プール", smtp.message.get_content())
        self.assertIn("現在の推定利用人数: 5人", smtp.message.get_content())
        self.assertIn("サイトの更新日時: 09/30 09:58", smtp.message.get_content())
        self.assertIn(
            "データ取得日時: 2026-09-30T10:00:00+09:00",
            smtp.message.get_content(),
        )


if __name__ == "__main__":
    unittest.main()
