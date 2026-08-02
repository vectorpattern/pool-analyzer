from pathlib import Path
import csv

DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "history.csv"

FIELDNAMES = [
    "timestamp",
    "updated",
    "status",
    "estimated",
    "state",
]


def get_last_record() -> dict | None:
    """CSVの最後の1件を取得する"""

    if not CSV_FILE.exists():
        return None

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return None

    return rows[-1]


def should_save(record: dict) -> bool:
    """保存が必要か判定する"""

    last = get_last_record()

    if last is None:
        return True

    return last["updated"] != record["updated"]


def save_record(record: dict) -> bool:
    """
    CSVへ保存する

    Returns
    -------
    bool
        True : 保存した
        False: 保存しなかった
    """

    if not should_save(record):
        return False

    DATA_DIR.mkdir(exist_ok=True)

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