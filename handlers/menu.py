from telegram import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes
from db import get_user


# 📥 Главное меню (используется после выбора маркетплейса)
async def send_main_menu(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, marketplace: str):
    user_id = query.from_user.id
    user = get_user(user_id)

    context.user_data["state"] = "main_menu"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Генерация названия и описания товара", callback_data="gen_menu")],
        [InlineKeyboardButton("💬 Генерация ответов на отзывы", callback_data="review_menu")],
        [InlineKeyboardButton("🔑 Анализ ключевых слов", callback_data="gen_keywords")],
        [InlineKeyboardButton("📘 Как пользоваться", callback_data="menu_help")],
        [InlineKeyboardButton("💳 Оплата и тарифы", callback_data="menu_pricing")],
        [InlineKeyboardButton("👤 Профиль", callback_data="menu_profile")],
        [InlineKeyboardButton("⚙️ Сменить маркетплейс", callback_data="start_interaction")]
    ])

    await query.edit_message_text(
        f"Отлично, работаем с {'Wildberries' if marketplace == 'wildberries' else 'Ozon'}!\n"
        f"Теперь можешь делегировать мне рутину. С чего начнем?\n\n"
        f"🎁 У тебя есть {user['requests_left']} бесплатных генерации.",
        reply_markup=keyboard
    )


# 🔄 Обработка переходов в меню (например, "профиль", "помощь")
async def menu_handler(update: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    if query.data == "menu_profile":
        tariff = "🆓 Бесплатный" if user["tariff"] == "free" else "💎 Премиум"
        left = user["requests_left"] if user["tariff"] == "free" else "∞"
        until = user["subscription_until"] if user["tariff"] == "premium" else "—"

        await query.edit_message_text(
            f"👤 *Профиль*\n"
            f"Тариф: {tariff}\n"
            f"Осталось генераций: {left}\n"
            f"Подписка до: {until}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧭 Главное меню", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_help":
        await query.edit_message_text(
            "📘 *Как пользоваться*\n\n"
            "1. Выбери маркетплейс\n"
            "2. Сгенерируй SEO-название, описание или ответ на отзыв\n"
            "3. Используй результат для продвижения своего товара 🚀\n\n"
            "Ты можешь использовать 3 генерации бесплатно, потом — премиум 😉",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧭 Главное меню", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_pricing":
        await query.edit_message_text(
            "💳 *Тарифы*\n\n"
            "Премиум за 1390 ₽ в месяц даёт тебе:\n"
            "• Безлимитные генерации SEO-текстов\n"
            "• Ответы на отзывы\n"
            "• Анализ ключевых слов\n\n"
            "🎁 Используй все 3 бесплатных генерации — и реши, хочешь ли продолжить!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Купить тариф", callback_data="menu_buy")],
                [InlineKeyboardButton("🧭 Главное меню", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_back":
        # Возврат в главное меню
        marketplace = user.get("marketplace", "wildberries")
        await send_main_menu(query, context, marketplace)