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
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1764885466374.jpg",
   "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/sketch-1765741210675.jpg"
]
# FINAL_MEDIA = "https://yadi.sk/i/final.gif"  # или .mp4
FINAL_MEDIA = "https://raw.githubusercontent.com/AndreyPuchinin/new_2026_happy_new_year_bot/main/поздравляшка.mp4"

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
# Фиксируем момент первого импорта модуля — это и есть "время старта теста"
_START_TIME = datetime.now()

# def get_current_test_day():
#    """Возвращает номер 'дня' с момента запуска бота (в тестовом режиме).
#    1 'день' = 1 минута.
#    """
#    now = datetime.now()
#    elapsed_seconds = (now - _START_TIME).total_seconds()
#    # Каждую 1 минуты = 60 секунд → новый "день"
#    day_number = int(elapsed_seconds // 60)
#    return f"test_day_{day_number}"
   
# def get_current_test_day():
#    now = datetime.now()
#    # Каждые 2 минуты — новый "день"
#    epoch = now - datetime(2025, 12, 1)  # базовая дата (начало ТЗ)
#    minutes_since_start = int(epoch.total_seconds() // 60)
#    test_day_number = minutes_since_start # // 1 # // 2  # каждые 2 минуты — новый день
#    return f"test_day_{test_day_number}"

# ========== ОТПРАВКА ПОЗДРАВЛЕНИЯ ВСЕМ ==========
async def send_new_year_to_all():
    """Отправляет НГ-поздравление ВСЕМ пользователям из Gist (один раз каждому)."""
    bot = Application.builder().token(BOT_TOKEN).build().bot  # создаём только bot-инстанс

    data = load_data()
    for user_id, user_data in data.items():
        if not user_data.get("has_received_final_greeting", False):
            try:
                await bot.send_animation(
                    chat_id=user_id,
                    animation=FINAL_MEDIA,
                    caption="🎆 С Новым годом! Пусть 2026 будет волшебным!"
                )
                # Обновляем флаг
                user_data["has_received_final_greeting"] = True
                save_data(data)
                logging.info(f"Поздравление отправлено пользователю {user_id}")
            except Exception as e:
                logging.error(f"Не удалось отправить пользователю {user_id}: {e}")

# ========== HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Получить попку 🍑"],
        ["Повторить приветствие"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "🎄 Бот Попкослатель\n\n"
        "Привет, я Попкослатель! 🍑\n\n"
        "У меня для тебя 14 новогодних попок. За день я могу прислать тебе всего 1 попку)\n\n"
        "Не пропускай дни и ты получишь максимум новогоднего настроения 🎄\n\n"
        "А если останешься со мной до нового года, ты получишь особое видео-поздравление от меня 🥂\n\n"
        "Подпишись на мой канал, чтобы оставаться со мной не только в рамках нового года и смотреть на попки круглый год:\n"
        "https://t.me/tacsolos\n\n"
        "А бота для меня сделал Андрей Кубик, вот его канал:\n"
        "https://t.me/AndyKybik\n\n"
        "Вперёд, к новым попкам!",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    # ==== ВЫЧИСЛЯЕМ ДЕНЬ (ТЕСТ) ИЛИ ДАТУ (ПРОД) ====
    TEST_MODE = False  # ← поменяй на False в продакшене!
    if TEST_MODE:
        today = get_current_test_day()  # например: "test_day_1"
        test_day_number = int(today.split("_")[-1])
        logging.info(f"test_day_number = {test_day_number}")
        is_new_year = test_day_number >= 2  # ← НГ на 2-й минуте
    else:
        # Московское время = UTC+3
        moscow_tz = timezone(timedelta(hours=3))
        today = datetime.now(moscow_tz).date().isoformat()
        is_new_year = date.today() >= date(2026, 1, 1)

    # ==== ЗАГРУЖАЕМ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ ====
    data = load_data()
    user = data.setdefault(user_id, {
        "last_claimed_date": None,
        "next_image_index": 0,
        "has_received_final_greeting": False
    })

    # ==== ФИНАЛЬНОЕ ПОЗДРАВЛЕНИЕ (1 РАЗ НА ПОЛЬЗОВАТЕЛЯ) ====
    if is_new_year and not user.get("has_received_final_greeting", False):
        logging.info("IN FINAL MEDIA")
        await update.message.reply_animation(
            FINAL_MEDIA,
            caption="🎆 С Новым годом! Пусть 2026 будет волшебным!"
        )
        user["has_received_final_greeting"] = True
        save_data(data)

    # ==== ОБРАБОТКА КНОПОК ====
    if text == "Повторить приветствие":
        await start(update, context)

    elif text == "Получить попку 🍑":
        if is_new_year:
            # После НГ — никаких картинок
            await update.message.reply_text("🎆 Вот и отгремел Новый 2026 Год! Время попок 🍑 закончилось :)")
        else:
            # До НГ — логика выдачи картинок
            if user["last_claimed_date"] == today:
                idx = user["next_image_index"]
                total_images = len(IMAGES)
                remaining = total_images - idx
                await update.message.reply_text(
                    f"Сегодняшняя попка 🍑 уже получена! {remaining} попок осталось."
                )
            else:
                idx = user["next_image_index"]
                total_images = len(IMAGES)
                remaining = total_images - idx
                if idx < total_images:
                    await update.message.reply_photo(
                        IMAGES[idx],
                        caption=f"🍑 Попка {idx + 1} из {total_images}. {remaining - 1} попок осталось."
                    )
                    user["last_claimed_date"] = today
                    user["next_image_index"] = idx + 1
                    if idx + 1 == total_images:
                        await update.message.reply_text("🎉 Ура! Ты собрал все попки! 🍑")
                    save_data(data)
                else:
                    await update.message.reply_text("🎉 Ты собрал все попки! 🍑")

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
