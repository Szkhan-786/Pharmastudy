import json
import random
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@Pharmastudy_in"  # Replace this
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Railway will provide this

app_flask = Flask(__name__)
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()


def load_topics():
    with open("topics.json", "r") as f:
        return json.load(f)


def load_progress():
    try:
        with open("progress.json", "r") as f:
            return json.load(f)
    except:
        return {"sent": [], "mode": 0, "current_topic": None}


def save_progress(data):
    with open("progress.json", "w") as f:
        json.dump(data, f)


async def send_mcq_answer(context: ContextTypes.DEFAULT_TYPE):
    topic = context.job.data
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"""✅ Answer:
{topic['mcq']['answer']}

📖 Explanation:
{topic['mcq']['explanation']}
"""
    )


async def send_content(context: ContextTypes.DEFAULT_TYPE):
    topics = load_topics()
    progress = load_progress()
    sent = progress["sent"]
    mode = progress["mode"]
    current_topic = progress["current_topic"]

    all_topics = []
    for unit in topics.values():
        for t in unit:
            if t["topic"] not in sent:
                all_topics.append(t)

    if not all_topics:
        progress["sent"] = []
        save_progress(progress)
        return

    if mode == 0 or not current_topic:
        topic = random.choice(all_topics)
        progress["current_topic"] = topic
    else:
        topic = current_topic

    if mode == 0:
        message = f"📚 Topic:\n{topic['topic']}"
    elif mode == 1:
        message = f"📝 Short Note:\n{topic['short_note']}"
    elif mode == 2:
        message = f"🧠 Viva:\n{topic['viva']}"
    elif mode == 3:
        options = "\n".join(topic["mcq"]["options"])
        message = f"❓ MCQ:\n{topic['mcq']['question']}\n\n{options}"
        context.job_queue.run_once(send_mcq_answer, 120, data=topic)
    else:
        message = f"🎯 10M Question:\n{topic['long_question']}"
        progress["sent"].append(topic["topic"])
        progress["current_topic"] = None

    progress["mode"] = (mode + 1) % 5
    save_progress(progress)

    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)


@app_flask.route("/", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"


@app_flask.route("/")
def home():
    return "Bot Running"


async def setup():
    await application.initialize()
    await bot.set_webhook(f"{WEBHOOK_URL}/")


if __name__ == "__main__":
    import asyncio
    asyncio.run(setup())
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
