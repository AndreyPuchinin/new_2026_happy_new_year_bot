import os
import json
import logging
import requests
from datetime import datetime, date
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
GIST_ID = os.environ["GIST_ID"]
GIST_TOKEN = os.environ["GIST_TOKEN"]
GIST_URL = f"https://api.github.com/gists/{GIST_ID}"

PORT = int(os.environ.get("PORT", 10000))
BOT_TOKEN = os.environ["BOT_TOKEN"]
DATA_FILE = Path("users.json")
IMAGES = [
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763678667830.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763678877771.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763680517099.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763682560118.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763741228535.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763741339403.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1763743851221.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764196038841.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764196842233.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764199126615.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764205314273.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764270762339.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764885466374.jpg"
]
# FINAL_MEDIA = "https://yadi.sk/i/final.gif"  # или .mp4
FINAL_MEDIA = "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764885466374.jpg"

# Flask-часть (не нужна)
# @bot.route('/ping')
# def ping():
#     return jsonify({"status": "alive", "bot": "new_year_bot"})

# ========== DATA HELPERS ==========
def load_data():
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    try:
        resp = requests.get(GIST_URL, headers=headers)
        content = resp.json()["files"]["users.json"]["content"]
        return json.loads(content)
    except:
        return {}

def save_data(data):
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    payload = {
        "files": {
            "users.json": {
                "content": json.dumps(data, ensure_ascii=False, indent=2)
            }
        }
    }
    requests.patch(GIST_URL, headers=headers, json=payload)
        
#========== TEMP TIME CHANGE FOR TESTS ==========
def get_current_test_day():
    now = datetime.now()
    # Каждые 2 минуты — новый "день"
    epoch = now - datetime(2025, 12, 1)  # базовая дата (начало ТЗ)
    minutes_since_start = int(epoch.total_seconds() // 60)
    test_day_number = minutes_since_start # // 1 # // 2  # каждые 2 минуты — новый день
    return f"test_day_{test_day_number}"

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
    today = get_current_test_day()
    # Извлекаем номер "дня" из строки
    test_day_number = int(today.split("_")[-1])
    # today = str(date.today())

    data = load_data()
    user = data.setdefault(user_id, {"last_claimed_date": None, "next_image_index": 0})

    if text == "Повторить приветствие":
        await start(update, context)

    elif text == "Получить картинку":
        idx = user["next_image_index"]
        total_images = len(IMAGES)
        remaining = total_images - idx  # ← вычисляем ДО if

        if user["last_claimed_date"] == today:
            await update.message.reply_text(f"🖼️ Картинка за сегодня уже получена! Осталось: {remaining-1}")
        elif idx < len(IMAGES):
            await update.message.reply_photo(IMAGES[idx], caption=f"🖼️ Картинка {idx + 1} из {total_images}. Осталось: {remaining-1}")
            user["last_claimed_date"] = today
            user["next_image_index"] = idx + 1
            save_data(data)
        if user["last_claimed_date"] == today and (idx >= len(IMAGES)):
            await update.message.reply_text("🎉 Ура! Ты собрал все картинки!")

            # === ФИНАЛЬНОЕ ПОЗДРАВЛЕНИЕ ===
            if not user.get("has_received_final_greeting", False):
               # ===== РЕЖИМ ТЕСТА =====
               TEST_MODE = True  # ← поменяй на False в продакшене!
               if TEST_MODE:
                  # Используем "тестовые дни"
                  test_day_number = int(today.split("_")[-1])
                  TEST_FINAL_DAY = 2  # ← поздравление на "день" №2 (т.е. через 2 минуты)
                  if test_day_number >= TEST_FINAL_DAY:
                     await update.message.reply_animation(
                            FINAL_MEDIA,
                            caption="🎆 С Новым годом! Пусть 2026 будет волшебным!"
                        )
                     user["has_received_final_greeting"] = True
                     save_data(data)
               # ===== РЕЖИМ ПРОДАКШЕНА =====
               else:
                  now = date.today()
                  FINAL_DATE = date(2026, 1, 1)
                  if now >= FINAL_DATE:
                     await update.message.reply_animation(
                        FINAL_MEDIA,
                        caption="🎆 С Новым годом! Пусть 2026 будет волшебным!"
                     )
                     user["has_received_final_greeting"] = True
                     save_data(data)

    else:
        await update.message.reply_text("Неизвестная команда. Используй кнопки ниже.")

# ========== MAIN ==========
def main():
    logging.basicConfig(level=logging.INFO)
    bot = Application.builder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    SERVICE_NAME = "new-2026-happy-new-year-bot"  # ← замени на имя твоего сервиса!
    service_webhook_url = f"https://{SERVICE_NAME}.onrender.com/{BOT_TOKEN}"
    
    # Webhook URL будет: https://<SERVICE_NAME>.onrender.com/<BOT_TOKEN>
    bot.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=service_webhook_url
    )

if __name__ == "__main__":
    main()
