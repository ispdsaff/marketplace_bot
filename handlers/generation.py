from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes
from db import get_user, decrement_requests
from prompts import generate_title_prompt, generate_description_prompt
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


async def generation_handler(update: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "gen_menu":
        context.user_data["state"] = None
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Название товара", callback_data="gen_title")],
            [InlineKeyboardButton("📄 Описание товара", callback_data="gen_description")],
            [InlineKeyboardButton("🧭 Главное меню", callback_data="menu_back")]
        ])
        await query.edit_message_text(
            "Название и описание — это не просто текст. Это твой шанс попасть в ТОП и увеличить продажи.\n\n"
            "Что сгенерируем сначала? 🚀",
            reply_markup=keyboard
        )

    elif query.data in ["gen_title", "gen_description"]:
        context.user_data["state"] = query.data
        label = "название" if query.data == "gen_title" else "описание"
        await query.edit_message_text(
            f"Отлично! Давай создадим SEO-{label}.\n\n"
            "Пожалуйста, отправь описание товара, его характеристики и ключевые слова 🔧\n\n"
            "_Пример: «Удобный рюкзак, водоотталкивающий, для города»_",
            parse_mode="Markdown"
        )


async def text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    text = update.message.text.strip()
    state = context.user_data.get("state")

    if state not in ["gen_title", "gen_description"]:
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

    # Подготовка промта
    if state == "gen_title":
        prompt = generate_title_prompt(text, user["marketplace"])
    else:
        prompt = generate_description_prompt(text, user["marketplace"])

    await update.message.reply_text("Секунду… думаю над лучшим вариантом ⏳")

    # Генерация через OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        result = response["choices"][0]["message"]["content"]
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка генерации: {e}")
        return

    # Учёт генерации
    if user["tariff"] == "free":
        decrement_requests(user_id)

    user = get_user(user_id)  # Обновлённые данные
    left = user["requests_left"] if user["tariff"] == "free" else "∞"
    result_message = f"Готово! Вот результат:\n\n{result}\n\nОсталось генераций: {left}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Ещё вариант", callback_data=state)],
        [InlineKeyboardButton("♻️ Новый товар", callback_data="gen_menu")],
        [InlineKeyboardButton("📊 Узнать про тарифы", callback_data="menu_pricing")],
        [InlineKeyboardButton("🧭 Главное меню", callback_data="menu_back")]
    ])

    await update.message.reply_text(result_message, reply_markup=keyboard)