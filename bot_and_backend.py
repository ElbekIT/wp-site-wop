# === bot_and_backend.py ===
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json, random, threading

TOKEN = "7607444887:AAHZu9rRTIMIuq4t__6dVkcwn64CXlDvy5w"  # <-- O'zingizning token bilan almashtiring
bot = Bot(token=TOKEN)

app = Flask(__name__)
codes = {}  # ID : code

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w") as f:
            json.dump(users, f)

    await update.message.reply_text("ID saqlandi! Saytga kirishda kerak bo‘ladi.")

@app.route("/send-code", methods=["POST"])
def send_code():
    user_id = str(request.json.get("telegram_id"))
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        return jsonify({"status": "error"}), 500

    if user_id in map(str, users):
        code = str(random.randint(100000, 999999))
        codes[user_id] = code
        try:
            bot.send_message(chat_id=user_id, text=f"Sizning tasdiqlash kodingiz: {code}")
            return jsonify({"status": "sent"})
        except Exception as e:
            return jsonify({"status": "bot_error", "error": str(e)}), 500
    return jsonify({"status": "not_allowed"}), 403

@app.route("/verify-code", methods=["POST"])
def verify_code():
    user_id = str(request.json.get("telegram_id"))
    code = request.json.get("code")
    if codes.get(user_id) == code:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 401

def run_bot():
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(port=5000)
