# Pool Analyzer

四街道市温水プールの混雑状況を収集・分析するプロジェクトです。

## 低混雑メール通知

推定利用人数が5人（サイト表示が「0～9人程」）になった時、前回の
`latest.json` が5人以外であればメールを1回送信します。5人程度の状態が
続いている間は再送しません。

メールはGoogle Apps Script（GAS）のWebアプリを経由して送信します。

### GASの設定

1. `gas/Code.gs` の内容でApps Scriptプロジェクトを作成します。
2. プロジェクト設定のスクリプトプロパティに以下を設定します。
   - `NOTIFICATION_EMAIL`: 通知を受け取るメールアドレス
   - `WEBHOOK_TOKEN`: 十分に長いランダム文字列
3. ウェブアプリとしてデプロイし、実行するユーザーを自分、アクセスできるユーザーを全員に設定します。

### GitHub Secrets

リポジトリのActions Secretsに以下を設定します。

- `GAS_WEB_APP_URL`: GAS Webアプリの`/exec` URL
- `GAS_WEBHOOK_TOKEN`: GASの`WEBHOOK_TOKEN`と同じ値

`Test GAS Email` ワークフローは、データ取得や保存を行わず、GAS経由のテストメールだけを送信します。

## 今後実装予定

- 利用人数の取得
- CSVへの保存
- GitHub Actionsによる5分ごとの自動取得
- 混雑分析
- グラフ表示
