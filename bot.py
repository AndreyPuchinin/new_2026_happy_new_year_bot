import os
import json
import logging
from datetime import datetime, date
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
PORT = int(os.environ.get("PORT", 10000))
BOT_TOKEN = os.environ["BOT_TOKEN"]
DATA_FILE = Path("users.json")
IMAGES = [
    "https://downloader.disk.yandex.ru/preview/57e5d12b8690c053675176f76e5bc3cf2af1ee7a7db584433f4c6c283a9421cd/693b67b4/YwLWCy3inpKx9a4ufnZLaj6BK0DHJrVHgyujT3ogvN4JrkZrsj8iNjlRd8uDHqvm6haDde4VTYNLKNhEtaPaow%3D%3D?uid=0&filename=sketch-1764885466374.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/6d8bf52f3399473b3237b9013ff64a38b2a070a2a767be22769a433b221857b5/693b67b4/21OU0VAtuamxv70ntxWoMv25LuELujKJyb7Aafrvp4veTuceJqJYL2lqA2kfnecLwY3rDVqk0eRMaN7g1x3vuw%3D%3D?uid=0&filename=sketch-1764270762339.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/f433e7cc1714f67564c6b74592f0e99bf6f4f7a1c80fd6c184b7a0dc333da861/693b67b4/0bdlWCJ7PhD85i1P_Ihul2VFPmKUTSS8kPj22HOoto5snKBm4mlldFx5jJnzB3iH2CgZgSIFvPzPM7nGxRazxQ%3D%3D?uid=0&filename=sketch-1764205314273.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/3c3625866405d6c941677965741679543e30c86edb45816b3f368f575cf2b040/693b67b4/zHBnLEysasVTz76K0pSUTiiG8KHvBtI8M5_LN0uTfkCX1Po4vU5zcxRDBQDgjNSpJTukfIjZZ0bKhfwtolievA%3D%3D?uid=0&filename=sketch-1764199126615.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/fae656e05409f806befdaaf95102cd833f2c8a74862598231a4b31a7ec0d07db/693b67b4/STZZtjGWI3xNIB86I0tgSD_0wk3vlT_9UCDMerwb1gDakEG5C12cnp316MeAc2pa-Y3lacPIdwpmR6kyGqG69A%3D%3D?uid=0&filename=sketch-1764196842233.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/71aa1a19c28ff3fdce188d41ac4ae83b2b2675a88f2614b9a7a4f20cb4c6452b/693b67b4/xu44BsUKPee4luLZ3PDUAj_0wk3vlT_9UCDMerwb1gD1zv0isteLDnVkHkXnamXwOscOEeaYE73qesggcROc7A%3D%3D?uid=0&filename=sketch-1764196038841.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/818806f3eed94bd25ad812e08c1f7877963328368550529696ed5b258a9eb051/693b67b4/PK_eusug_NCDf7zRrUvHVNrxUwKcvalbOhvJ2QGL6kZo9saSQr5xvBuSVZCRDdcHfiMFRaj0hbIJJcbH0WTN6w%3D%3D?uid=0&filename=sketch-1763743851221.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/262b7de4b2fab7a99e0c8a7647a766ffd558b7a530542d83e632a78ed4bb07bb/693b67b4/0bdlWCJ7PhD85i1P_Ihul4lGmH-ypU-1sw__AzIS6Jww-FfLq4nVdArzk38_-2nBGJeMDL8hNNe3WCvp3n1u2A%3D%3D?uid=0&filename=sketch-1763741339403.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/f2eb145a49a33a4563adad5dc7ccccd63bff7648cf6ece2f5d8dfe3b68d68830/693b67b4/ltv0F6evVaMI7J9rHi5TKNrxUwKcvalbOhvJ2QGL6kbDlnsvgJpac5qLc-X9RXGiwZ-E9A5W7xqQEda8k3R-rw%3D%3D?uid=0&filename=sketch-1763741228535.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/13439b41642c0f5fc1bfd6af08e851a6f7ac54dffb02712c7244307083f47dc1/693b67b4/YD1BOBe22tKkMtAL4ZoIZHvkKC-eP2jaYFNc-UnPLnA1l4cVkSol4sTNqHGrTX1oHmu9DLf4mLMxf_tgGo60MA%3D%3D?uid=0&filename=sketch-1763682560118.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/38a234dd71665a1a82801070f04fe38a9418660b692df32f2e3ddebe09b37a3a/693b67b4/rx6bKC33D2TVPPhGRav1aLSYgkmcePZpB_9GVxAyx_wo4ApeKEDcRphSTP-3bOjZo4EDvtxCX7zhRAR2gel-iQ%3D%3D?uid=0&filename=sketch-1763680517099.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/bdd764a5fdfca38160c271823df06b228c4042435c8d11ce459337d95f22dcc2/693b67b4/QMAu0FpClKDbz_gOvI88LMuFy4BnMWpxEl0thJDxXO5wrh9N_SdaI7tWUlmrm9bTkC-LnqLc2I8ADz4cvtdJyQ%3D%3D?uid=0&filename=sketch-1763678877771.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    "https://downloader.disk.yandex.ru/preview/19eb2ab206e7b45a42fd76914282c1ab253c0afc9f956612375e6bfacd2cd02d/693b67b4/Rpp2SJB1b8U2X7TjKcU9RdrxUwKcvalbOhvJ2QGL6kZq1lXzaaB8pAFaOwFQGQyE8z5MRXKLkeOAIfUuWHPvow%3D%3D?uid=0&filename=sketch-1763678667830.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838",
    
]
# FINAL_MEDIA = "https://yadi.sk/i/final.gif"  # или .mp4
FINAL_MEDIA = "https://downloader.disk.yandex.ru/preview/19eb2ab206e7b45a42fd76914282c1ab253c0afc9f956612375e6bfacd2cd02d/693b67b4/Rpp2SJB1b8U2X7TjKcU9RdrxUwKcvalbOhvJ2QGL6kZq1lXzaaB8pAFaOwFQGQyE8z5MRXKLkeOAIfUuWHPvow%3D%3D?uid=0&filename=sketch-1763678667830.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=1920x838"

# Flask-часть (не нужна)
# @bot.route('/ping')
# def ping():
#     return jsonify({"status": "alive", "bot": "new_year_bot"})

# ========== DATA HELPERS ==========
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
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
    # today = str(date.today())

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
            # if now.year == 2026 and datetime.now().month == 1 and datetime.now().day == 1:
            TEST_FINAL_DAY = 5  # например, на "день" №100 — показывать гифку
            if test_day_number >= TEST_FINAL_DAY:
                await update.message.reply_animation(
                    FINAL_MEDIA,
                    caption="🎆 С Новым годом! Пусть 2026 будет волшебным!"
                )

    else:
        await update.message.reply_text("Неизвестная команда. Используй кнопки ниже.")

# ========== MAIN ==========
def main():
    logging.basicConfig(level=logging.INFO)
    bot = Application.builder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook URL будет: https://your-app.onrender.com/<BOT_TOKEN>
    bot.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://your-app.onrender.com/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
