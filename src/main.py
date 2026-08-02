from src.fetch import fetch_pool_status
from src.storage import save_record


def print_record(record: dict) -> None:
    print("=" * 40)
    print("四街道市温水プール 利用状況")
    print("=" * 40)

    for key, value in record.items():
        print(f"{key:10}: {value}")


def main():

    record = fetch_pool_status()

    saved = save_record(record)

    print_record(record)
    print()

    if saved:
        print("history.csv を更新しました。")
    else:
        print("latest.json のみ更新しました。（履歴に変更なし）")


if __name__ == "__main__":
    main()