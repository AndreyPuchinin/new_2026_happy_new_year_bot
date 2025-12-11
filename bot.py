import os
import json
import logging
from datetime import datetime, date
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, jsonify  # <-- Добавили Flask

# ========== CONFIG ==========
BOT_TOKEN = os.environ["BOT_TOKEN"]
DATA_FILE = Path("users.json")
IMAGES = [
    "https://downloader.disk.yandex.ru/preview/19eb2ab206e7b45a42fd76914282c1ab253c0afc9f956612375e6bfacd2cd02d/693b67b4/Rpp2SJB1b8U2X7TjKcU9RdrxUwKcvalbOhvJ2QGL6kZq1lXzaaB8pAFaOwFQGQyE8z5MRXKLkeOAIfUuWHPvow%3D%3D?uid=0&filename=sketch-1763678667830.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763678667830.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763678877771.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763680517099.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763682560118.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763741228535.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763741339403.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1763743851221.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1764196038841.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1764196842233.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1764199126615.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1764205314273.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1764270762339.jpg",
    "https://disk.yandex.ru/d/y7vrmCpcQaGJvA/sketch-1764885466374.jpg"
]
# FINAL_MEDIA = "https://yadi.sk/i/final.gif"  # или .mp4
FINAL_MEDIA = ""
# ========== FLASK SERVER (для Render) ==========
app = Flask(__name__)

@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "bot": "new_year_bot"})

# ========== DATA HELPERS ==========
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Получить картинку"],
        ["Повторить приветствие"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "🎄 Бот Попкослатель\n\n"
        "Привет, я Попкослатель! 🍑\n\n"
        "У меня для тебя 14 новогодних попок. За день я могу прислать тебе всего 1 попку)\n\n"
        "Не пропускай дни и ты получишь максимум новогоднего настроения 🎄\n\n"
        "А если останешься со мной до нового года, ты получишь особое видео-поздравление от меня 🥂\n\n"
        "Вперёд, к новым попкам!",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    today = str(date.today())

    data = load_data()
    user = data.setdefault(user_id, {"last_claimed_date": None, "next_image_index": 0})

    if text == "Повторить приветствие":
        await start(update, context)

    elif text == "Получить картинку":
        if user["last_claimed_date"] == today:
            await update.message.reply_text("🖼️ Картинка за сегодня уже получена!")
        else:
            idx = user["next_image_index"]
            if idx < len(IMAGES):
                await update.message.reply_photo(IMAGES[idx])
                user["last_claimed_date"] = today
                user["next_image_index"] = idx + 1
                save_data(data)
            else:
                await update.message.reply_text("🎉 Ура! Ты собрал все картинки!")

            # Проверка: сегодня 31 декабря?
            if datetime.now().month == 12 and datetime.now().day == 31:
                await update.message.reply_animation(
                    FINAL_MEDIA,
                    caption="🎆 С Новым годом! Пусть 2026 будет волшебным!"
                )

    else:
        await update.message.reply_text("Неизвестная команда. Используй кнопки ниже.")

# ========== MAIN ==========
def main():
    logging.basicConfig(level=logging.INFO)
    app_telegram = Application.builder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем Flask в отдельном потоке
    from threading import Thread
    thread = Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False, use_reloader=False))
    thread.daemon = True
    thread.start()

    # Запускаем Telegram-бота
    app_telegram.run_polling()

if __name__ == "__main__":
    main()
