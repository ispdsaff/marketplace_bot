import os
import logging
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from db import init_db
from handlers import start, menu, generation, review, fallback

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_SERVICE_NAME = os.getenv("RENDER_SERVICE_NAME")
PORT = int(os.getenv("PORT", 8000))
WEBHOOK_URL = f"https://{RENDER_SERVICE_NAME}.onrender.com/{BOT_TOKEN}"


def main():
    # 📦 Инициализация базы данных
    init_db()

    # ⚙️ Создание Telegram-приложения
    application = Application.builder().token(BOT_TOKEN).build()

    # 🔍 Хендлер для отладки — вывод всех апдейтов
    async def debug_handler(update, context):
        print("📝 Получено сообщение:", update)

    # 🧩 Регистрация хендлеров
    application.add_handler(CommandHandler("start", start.start_handler))
    application.add_handler(CallbackQueryHandler(start.callback_handler, pattern="^start_interaction$|^market_"))
    application.add_handler(CallbackQueryHandler(menu.callback_handler, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(generation.callback_handler, pattern="^generate_"))
    application.add_handler(CallbackQueryHandler(review.callback_handler, pattern="^review_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback.fallback_handler))
    application.add_handler(MessageHandler(filters.ALL, debug_handler))

    # 🚀 Запуск вебхука
    aapplication.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://{RENDER_SERVICE_NAME}.onrender.com/{BOT_TOKEN}"
)


if __name__ == "__main__":
    main()