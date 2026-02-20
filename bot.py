import json
import random
import asyncio
import os
from telegram import Bot
from telegram.ext import ApplicationBuilder

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@Pharmastudy_in"  # Replace this

bot = Bot(token=TOKEN)


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


async def send_mcq_answer(topic):
    await asyncio.sleep(120)
    answer_text = f"""✅ Answer:
{topic['mcq']['answer']}

📖 Explanation:
{topic['mcq']['explanation']}
"""
    await bot.send_message(chat_id=CHANNEL_ID, text=answer_text)


async def send_content():
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
        asyncio.create_task(send_mcq_answer(topic))
    else:
        message = f"🎯 10M Question:\n{topic['long_question']}"
        progress["sent"].append(topic["topic"])
        progress["current_topic"] = None

    progress["mode"] = (mode + 1) % 5
    save_progress(progress)

    await bot.send_message(chat_id=CHANNEL_ID, text=message)


async def scheduler(app):
    while True:
        await send_content()
        await asyncio.sleep(1800)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Start scheduler after bot starts
    async def post_init(application):
        asyncio.create_task(scheduler(application))

    app.post_init = post_init

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
