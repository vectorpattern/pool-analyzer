from datetime import datetime
from zoneinfo import ZoneInfo
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

URL = "http://yotsu-foundation.or.jp/onpool/"


def create_session() -> requests.Session:
    """リトライ設定済みのSessionを作成する"""

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def estimate_people_count(status: str) -> int | None:
    """
    利用状況から推定人数を返す。

    例
        0～9人程   -> 5
        30～39人程 -> 35
        90～99人程 -> 95
        100人以上  -> 100
    """

    match = re.search(r"(\d+)～(\d+)人", status)

    if match:
        lower = int(match.group(1))
        return lower + 5

    if "100人以上" in status:
        return 100

    return None


def get_state(status: str) -> str:
    """営業状態を返す"""

    if "入場中" in status:
        return "OPEN"

    if "営業時間外" in status:
        return "CLOSED"

    return "HOLIDAY"


def fetch_pool_status() -> dict:
    """プール利用状況を取得する"""

    session = create_session()

    response = session.get(URL, timeout=10)
    response.raise_for_status()

    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")

    # -----------------------------
    # 更新日時
    # -----------------------------
    updated = ""

    for p in soup.find_all("p", class_="label"):
        text = p.get_text(" ", strip=True)

        if "更新日時：" in text:
            updated = text.split("更新日時：")[-1]
            break

    # -----------------------------
    # 利用状況
    # -----------------------------
    status = "休業日"

    for p in soup.find_all("p", class_="center"):
        text = p.get_text(strip=True)

        if "入場中" in text:
            status = text
            break

        if "営業時間外" in text:
            status = text
            break

    record = {
        "timestamp": datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).isoformat(timespec="seconds"),

        "updated": updated,

        "status": status,

        "estimated": estimate_people_count(status),

        "state": get_state(status),
    }

    return record


if __name__ == "__main__":
    print(fetch_pool_status())