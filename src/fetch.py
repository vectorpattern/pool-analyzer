import requests
from bs4 import BeautifulSoup

URL = "http://yotsu-foundation.or.jp/onpool/"


def fetch_pool_status():
    """プール利用状況を取得する"""

    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    # 日本語サイト対策
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")

    # -----------------------------
    # 更新日時を取得
    # -----------------------------
    updated = ""

    for p in soup.find_all("p", class_="label"):
        text = p.get_text(" ", strip=True)

        if "更新日時：" in text:
            updated = text.split("更新日時：")[-1]
            break

    # -----------------------------
    # 利用状況を取得
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

    return updated, status

import re

def estimate_people_count(status: str) -> int | None:
    """
    利用状況の文字列から推定人数を返す。

    例:
        0～9人程、入場中です   -> 5
        30～39人程、入場中です -> 35
        90～99人程、入場中です -> 95
        100人以上             -> 100
        営業時間外です         -> None
        休業日                -> None
    """

    # 「〇～〇人程」を取得
    match = re.search(r"(\d+)～(\d+)人", status)

    if match:
        lower = int(match.group(1))
        return lower + 5

    # 「100人以上」
    if "100人以上" in status:
        return 100

    # 営業時間外・休業日など
    return None

def main():
    updated, status = fetch_pool_status()
    estimated = estimate_people_count(status)

    print("=" * 40)
    print("四街道市温水プール 利用状況")
    print("=" * 40)
    print(f"更新日時 : {updated}")
    print(f"利用状況 : {status}")
    print(f"推定人数 : {estimated}")

if __name__ == "__main__":
    main()