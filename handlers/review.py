from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes
from db import get_user, decrement_requests
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


async def review_handler(update: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "review_menu":
        context.user_data["state"] = "review_prepare"
        await query.edit_message_text(
            "Отлично! Давай подготовим ответ на отзыв 🧾\n\n"
            "Пожалуйста, пришли:\n"
            "• Название товара\n"
            "• Текст отзыва\n\n"
            "В одном сообщении. Пример:\n\n"
            "*Кроссовки Puma RS-X*\nОчень удобные, но пришли без шнурков.",
            parse_mode="Markdown"
        )

    elif query.data == "review_menu_again":
        context.user_data["state"] = "review_prepare"
        await query.edit_message_text(
            "Пришли название товара и текст нового отзыва 📝"
        )


async def text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    state = context.user_data.get("state")

    if state != "review_prepare":
        return

    if user["tariff"] == "free" and user["requests_left"] <= 0:
        await update.message.reply_text(
            "😔 У тебя закончились бесплатные генерации.\n\n"
            "Подключи премиум, чтобы продолжить 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Узнать про тарифы", callback_data="menu_pricing")]
            ])
        )
        return

    text = update.message.text.strip()
    parts = text.split("\n", 1)

    if len(parts) < 2:
        await update.message.reply_text(
            "Хм… кажется, ты указал слишком мало информации 🧐\n\n"
            "Пожалуйста, укажи и *название товара*, и *текст отзыва* в одном сообщении.",
            parse_mode="Markdown"
        )
        return

    product_name, review_text = parts[0].strip(), parts[1].strip()

    prompt = (
        f"Сгенерируй вежливый, профессиональный и доброжелательный ответ на отзыв покупателя.\n\n"
        f"Товар: {product_name}\n"
        f"Отзыв: {review_text}\n\n"
        f"Сделай так, чтобы показать заботу о клиенте, и чтобы другие увидели, что продавец — профи."
    )

    await update.message.reply_text("Думаю над идеальным ответом… 💬⏳")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        result = response["choices"][0]["message"]["content"]
    except Exception as e:
        await update.message.reply_text(f"Ошибка генерации ответа: {e}")
        return

    if user["tariff"] == "free":
        decrement_requests(user_id)

    user = get_user(user_id)
    left = user["requests_left"] if user["tariff"] == "free" else "∞"

    result_text = f"Вот как можно ответить 👇\n\n{result}\n\nОсталось генераций: {left}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Ещё вариант", callback_data="review_menu")],
        [InlineKeyboardButton("♻️ Новый отзыв", callback_data="review_menu_again")],
        [InlineKeyboardButton("🧭 Главное меню", callback_data="menu_back")]
    ])

    await update.message.reply_text(result_text, reply_markup=keyboard)