from telegram import Update
from telegram.ext import ContextTypes


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if message.text:
        text = message.text.strip()

        # Слишком короткое сообщение
        if len(text) < 10:
            await message.reply_text(
                "Спасибо! Но если получится — пришли чуть больше контекста 🙏\n"
                "Опиши товар, его особенности, ключевые слова — чем больше, тем лучше результат! 💡"
            )
        # Пользователь отправил ссылку
        elif "http://" in text or "https://" in text:
            await message.reply_text(
                "🧩 Пока я не умею распознавать информацию по ссылке.\n"
                "Напиши текстом, что за товар или отзыв — и я помогу тебе по полной! 🚀"
            )
        # Если нет активного состояния
        else:
            await message.reply_text(
                "Я пока не понял, что ты хочешь сгенерировать 🤖\n"
                "Выбери действие в меню и отправь нужную информацию ещё раз.",
            )

    # Фото / документ
    elif message.photo or message.document:
        await message.reply_text(
            "🖼️ Картинки я пока не распознаю (на стадии MVP).\n"
            "Опиши товар словами — и я подготовлю текст не хуже топ-селлеров!"
        )

    # Голосовое / аудио
    elif message.voice or message.audio:
        await message.reply_text(
            "🎙️ Голосовые пока вне зоны доступа 😅\n"
            "Пожалуйста, напиши описание или отзыв в текстовом виде."
        )

    # Всё остальное
    else:
        await message.reply_text(
            "Не совсем понял… 😶 Пожалуйста, отправь текстовое описание или воспользуйся кнопками меню."
        )