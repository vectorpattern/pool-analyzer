import os
import smtplib
from collections.abc import Callable, Mapping
from email.message import EmailMessage


def should_send_low_capacity_notification(
    record: dict, previous_record: dict | None
) -> bool:
    """低混雑への遷移時に通知すべきか判定する。"""

    previous_estimated = (
        previous_record.get("estimated") if previous_record is not None else None
    )

    return (
        record.get("state") == "OPEN"
        and record.get("estimated") == 5
        and previous_estimated != 5
    )


def create_notification_message(record: dict, sender: str, recipient: str) -> EmailMessage:
    """低混雑通知メールを作成する。"""

    message = EmailMessage()
    message["Subject"] = "四街道市温水プール：低混雑のお知らせ"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "四街道市温水プールの利用状況が0～9人程になりました。\n\n"
        f"現在の推定利用人数: {record['estimated']}人\n"
        f"サイトの更新日時: {record['updated']}\n"
        f"データ取得日時: {record['timestamp']}\n"
    )

    return message


def send_low_capacity_notification(
    record: dict,
    smtp_factory: Callable[..., smtplib.SMTP] = smtplib.SMTP,
    environ: Mapping[str, str] | None = None,
) -> None:
    """環境変数のSMTP設定を使って低混雑通知メールを送信する。"""

    settings = os.environ if environ is None else environ
    host = settings["SMTP_HOST"]
    port = int(settings["SMTP_PORT"])
    username = settings["SMTP_USERNAME"]
    password = settings["SMTP_PASSWORD"]
    sender = settings["MAIL_FROM"]
    recipient = settings["MAIL_TO"]

    message = create_notification_message(record, sender, recipient)
    smtp = smtp_factory(host, port)

    try:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)
    finally:
        smtp.quit()
