function doPost(e) {
  const data = e && e.parameter ? e.parameter : {};
  const expectedToken = PropertiesService.getScriptProperties().getProperty(
    "WEBHOOK_TOKEN"
  );
  const notificationEmail = PropertiesService.getScriptProperties().getProperty(
    "NOTIFICATION_EMAIL"
  );

  if (!expectedToken || data.token !== expectedToken) {
    return createJsonResponse({ status: "error", message: "unauthorized" });
  }

  if (!notificationEmail) {
    return createJsonResponse({
      status: "error",
      message: "NOTIFICATION_EMAIL is not configured",
    });
  }

  const isTest = data.is_test === "true";
  const subject = isTest
    ? "【テスト】四街道市温水プール：GAS送信確認"
    : "【四街道市温水プール】今がチャンスです！";
  const body =
    (isTest ? "これはGAS経由のテストメールです。\n\n" : "") +
    "四街道市温水プールの利用状況が0～9人程になりました。\n\n" +
    "サイトの更新日時: " + data.updated + "\n" +
    "データ取得日時: " + data.timestamp + "\n";

  try {
    MailApp.sendEmail(notificationEmail, subject, body);
    return createJsonResponse({ status: "success" });
  } catch (error) {
    console.error(error);
    return createJsonResponse({ status: "error", message: error.message });
  }
}


function createJsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(
    ContentService.MimeType.JSON
  );
}
