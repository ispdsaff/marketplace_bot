from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from db import get_user, create_user, update_marketplace
from handlers.menu import send_main_menu


# Хендлер на команду /start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Начать взаимодействие", callback_data="start_interaction")]
    ])

    await update.message.reply_text(
        "Привет, я Марк 👋\n"
        "Я здесь, чтобы взять на себя твою рутину:\n"
        "— придумаю название и описание товара\n"
        "— вежливо отвечу на отзывы\n"
        "— изучу конкурентов\n\n"
        "🎁 У тебя есть 3 бесплатные генерации, чтобы убедиться, что мы сработаемся.\n"
        "Погнали?",
        reply_markup=keyboard
    )


# Обработка кнопки "🚀 Начать взаимодействие" и выбор маркетплейса
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_interaction":
        # Запоминаем, что ждём выбор маркетплейса
        context.user_data["state"] = "awaiting_marketplace"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟣 Wildberries", callback_data="market_wb")],
            [InlineKeyboardButton("🔵 Ozon", callback_data="market_ozon")]
        ])

        await query.edit_message_text(
            "Чтобы мои подсказки и генерации были максимально точными, нужно знать одну деталь:\n\n"
            "Где ты продаёшь? WB или Ozon?\nВыбери ниже 👇",
            reply_markup=keyboard
        )

    elif query.data.startswith("market_"):
        user_id = query.from_user.id
        marketplace = "wildberries" if "wb" in query.data else "ozon"

        # Создание или обновление пользователя в БД
        if get_user(user_id):
            update_marketplace(user_id, marketplace)
        else:
            create_user(user_id, marketplace)

        context.user_data["marketplace"] = marketplace
        context.user_data["state"] = "main_menu"

        # Переход в главное меню
        await send_main_menu(query, context, marketplace)