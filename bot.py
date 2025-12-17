from flask import Flask, request
import requests
import json
import pandas as pd
import time
import os
import threading

# =============================
# CONFIG
# =============================
app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = "https://rossmann-api-ekwe.onrender.com/rossmann/predict"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "data")
TEST_FILE = os.path.join(DATA_PATH, "test.csv")
STORE_FILE = os.path.join(DATA_PATH, "store.csv")


REQUEST_INTERVAL = 5  # seconds (rate limit per user)
last_request_time = {}

USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"


# =============================
# TELEGRAM HELPERS
# =============================
def send_message(chat_id, text):
    url = f"{TELEGRAM_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload, timeout=10)


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset

    r = requests.get(url, params=params)
    return r.json()


# =============================
# DATA & MODEL
# =============================
def load_dataset(store_id):
    df_test = pd.read_csv(TEST_FILE)
    df_store = pd.read_csv(STORE_FILE)

    if store_id not in df_store["Store"].unique():
        return "not_found"

    df = pd.merge(df_test, df_store, how="left", on="Store")
    df = df[df["Store"] == store_id]
    df = df[df["Open"] == 1]

    if df.empty:
        return "closed"

    df = df.drop("Id", axis=1)
    return json.dumps(df.to_dict(orient="records"))


def predict(data):
    headers = {"Content-type": "application/json"}

    try:
        r = requests.post(API_URL, data=data, headers=headers, timeout=10)
    except requests.exceptions.RequestException:
        return "service_down"

    if r.status_code != 200:
        return "service_down"

    return pd.DataFrame(r.json())


# =============================
# UTILS
# =============================
def format_currency(value):
    #return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") #change currency, rossmann uses euro


def extract_store_ids(text):
    text = text.replace("/", "").replace(" ", "")
    parts = text.split(",")
    return list({int(p) for p in parts if p.isdigit()})


# =============================
# BOT MESSAGES
# =============================
def start_message():
    return (
        "<b>👋 Welcome to the Rossmann Sales Forecast Bot</b>\n\n"
        "Predict sales for the next <b>6 weeks</b>.\n\n"
        "<b>Usage:</b>\n"
        "• Single store: 25\n"
        "• Multiple stores: 25,3,6,8\n\n"
        "ℹ️ Type /help for details."
    )


def help_message():
    return (
        "<b>ℹ️ Help</b>\n\n"
        "Send one or more store numbers.\n\n"
        "<b>Responses:</b>\n"
        "💰 Prediction\n"
        "🚫 Closed store\n"
        "❓ Store not found\n\n"
        "📅 Horizon: <b>6 weeks</b>"
    )


# =============================
# CORE MESSAGE HANDLER
# =============================
def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    now = time.time()
    last_time = last_request_time.get(chat_id, 0)

    if now - last_time < REQUEST_INTERVAL:
        send_message(
            chat_id,
            "⏳ <b>Please wait a few seconds</b> before sending another request."
        )
        return

    last_request_time[chat_id] = now

    if text.lower() == "/start":
        send_message(chat_id, start_message())
        return

    if text.lower() == "/help":
        send_message(chat_id, help_message())
        return

    store_ids = extract_store_ids(text)

    if not store_ids:
        send_message(chat_id, "❌ <b>Invalid input.</b> Type /help.")
        return

    send_message(chat_id, "⏳ <b>Processing your request...</b>")

    results = []
    valid_sales = {}
    closed_count = 0
    not_found_count = 0

    for store_id in store_ids:
        data = load_dataset(store_id)

        if data == "not_found":
            not_found_count += 1
            results.append(f"🏪 Store {store_id}: ❓ <b>not found</b>")
            continue

        if data == "closed":
            closed_count += 1
            results.append(f"🏪 Store {store_id}: 🚫 <b>closed</b>")
            continue

        df_pred = predict(data)

        if isinstance(df_pred, str) and df_pred == "service_down":
            results.append(
                f"🏪 Store {store_id}: ⚠️ <b>service unavailable</b>"
            )
            continue

        total = df_pred["prediction"].sum()
        valid_sales[store_id] = total

        results.append(
            f"🏪 Store {store_id}: 💰 <b>{format_currency(total)}</b>"
        )

    if len(store_ids) > 1 and valid_sales:
        sorted_sales = sorted(valid_sales.items(), key=lambda x: x[1], reverse=True)
        total_sum = sum(valid_sales.values())

        summary = (
            "\n\n<b>📊 Summary</b>\n"
            f"• Valid predictions: <b>{len(valid_sales)}</b>\n"
            f"• Closed stores: <b>{closed_count}</b>\n"
            f"• Not found: <b>{not_found_count}</b>\n\n"
            f"💰 <b>Total expected:</b> {format_currency(total_sum)}"
        )

        if len(sorted_sales) >= 2:
            top1, top2 = sorted_sales[0], sorted_sales[1]
            diff = top1[1] - top2[1]

            summary += (
                f"\n\n🏆 <b>Top store:</b> {top1[0]} "
                f"({format_currency(top1[1])})\n"
                f"🥈 <b>Second:</b> {top2[0]} "
                f"({format_currency(top2[1])})\n"
                f"📉 <b>Difference:</b> {format_currency(diff)}"
            )

        results.append(summary)

    send_message(chat_id, "\n".join(results))


# =============================
# WEBHOOK ROUTES (PRODUÇÃO)
# =============================
@app.route("/", methods=["GET"])
def health():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        handle_message(update["message"])

    return "OK", 200


# =============================
# POLLING (LOCAL)
# =============================
def polling():
    print("🤖 Rossmann bot running...")
    offset = None

    while True:
        updates = get_updates(offset)

        if not updates.get("ok"):
            time.sleep(5)
            continue

        for update in updates["result"]:
            offset = update["update_id"] + 1

            if "message" in update:
                handle_message(update["message"])

        time.sleep(2)


# =============================
# RUN
# =============================
if __name__ == "__main__":
    if USE_WEBHOOK:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        polling()