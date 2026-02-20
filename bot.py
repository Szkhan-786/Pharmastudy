import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

def load_topics():
    with open("topics.json", "r") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📘 Welcome to B.Pharm Mentor Bot")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = load_topics()
    unit = random.choice(list(topics.keys()))
    topic = random.choice(topics[unit])

    message = f"""
📚 Unit: {unit}

🎯 Topic: {topic['topic']} ({topic['marks']})

🧠 Viva:
{topic['viva']}
"""
    await update.message.reply_text(message)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", daily))

app.run_polling()
