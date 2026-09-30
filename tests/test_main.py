import unittest
from unittest.mock import patch

from src import main


class MainTests(unittest.TestCase):
    def test_does_not_save_when_notification_fails(self) -> None:
        record = {"estimated": 5, "state": "OPEN"}

        with (
            patch.object(main, "fetch_pool_status", return_value=record),
            patch.object(main, "get_latest_record", return_value={"estimated": 15}),
            patch.object(main, "should_send_low_capacity_notification", return_value=True),
            patch.object(
                main,
                "send_low_capacity_notification",
                side_effect=RuntimeError("SMTP failed"),
            ),
            patch.object(main, "save_record") as save_record,
        ):
            with self.assertRaisesRegex(RuntimeError, "SMTP failed"):
                main.main()

        save_record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
