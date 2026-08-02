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


def save_record(record: dict) -> None:
    """CSVへ1件保存する"""

    DATA_DIR.mkdir(exist_ok=True)

    file_exists = CSV_FILE.exists()

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)