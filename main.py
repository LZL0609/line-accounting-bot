from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

balance = 0

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global balance
    text = event.message.text.strip()
    reply = ""

    if text.startswith('+') or text.startswith('-'):
        try:
            amt = int(text.split(' ')[0])
            note = ' '.join(text.split(' ')[1:])
            balance += amt
            reply = f"✅ 記帳成功：{amt}（{note}）\n目前餘額：{balance} 元"
        except:
            reply = "⚠️ 請用格式：+100 早餐 或 -50 咖啡"
    elif text == '查餘額':
        reply = f"📌 目前餘額：{balance} 元"
    else:
        reply = "請輸入 +金額 類別 或 '查餘額' 查詢"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
