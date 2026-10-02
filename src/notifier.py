import os
from collections.abc import Callable, Mapping

import requests


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


def send_low_capacity_notification(
    record: dict,
    post: Callable[..., requests.Response] = requests.post,
    environ: Mapping[str, str] | None = None,
    is_test: bool = False,
) -> None:
    """GAS Webアプリを経由して低混雑通知メールを送信する。"""

    settings = os.environ if environ is None else environ
    response = post(
        settings["GAS_WEB_APP_URL"],
        data={
            "token": settings["GAS_WEBHOOK_TOKEN"],
            "estimated": str(record["estimated"]),
            "updated": record["updated"],
            "timestamp": record["timestamp"],
            "is_test": str(is_test).lower(),
        },
        timeout=10,
    )
    response.raise_for_status()

    result = response.json()

    if result.get("status") != "success":
        message = result.get("message", "GASがメール送信に失敗しました。")
        raise RuntimeError(message)
