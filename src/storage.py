import csv
import json
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))

CSV_FILE = DATA_DIR / "history.csv"
LATEST_FILE = DATA_DIR / "latest.json"

FIELDNAMES = [
    "timestamp",
    "updated",
    "status",
    "estimated",
    "state",
]


def get_last_record() -> dict | None:
    """history.csv の最後の1件を取得する"""

    if not CSV_FILE.exists():
        return None

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return None

    return rows[-1]


def should_save(record: dict) -> bool:
    """
    history.csvへ保存する必要があるか判定する

    サイトの更新日時(updated)が変わった時だけ保存する。
    """

    last = get_last_record()

    if last is None:
        return True

    return last["updated"] != record["updated"]


def save_latest(record: dict) -> None:
    """
    最新状態を latest.json に保存する。

    毎回上書きする。
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        json.dump(
            record,
            f,
            ensure_ascii=False,
            indent=2,
        )


def save_history(record: dict) -> bool:
    """
    history.csvへ保存する。

    Returns
    -------
    bool
        True : 保存した
        False: 保存しなかった
    """

    if not should_save(record):
        return False

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = CSV_FILE.exists()

    with open(CSV_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)

    return True


def save_record(record: dict) -> bool:
    """
    取得データを保存する。

    latest.json は毎回更新。
    history.csv は更新があった時だけ追記。
    """

    save_latest(record)

    return save_history(record)