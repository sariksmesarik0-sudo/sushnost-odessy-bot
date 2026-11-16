import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL = os.getenv("CHANNEL_ID")

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "⚓ Добро пожаловать в предложку «Сущность Одессы»!\n\n"
        "Отправь фото, видео или текст. Администратор проверит материал."
    )

@dp.message(Command("myid"))m
async def myid(message: Message):
    await message.answer(f"Твой ID: <code>{message.from_user.id}</code>")

@dp.message(F.chat.type == "private")
async def proposal(message: Message):
    if not message.text and not message.photo and not message.video and not message.document:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Опубликовать", callback_data="approve"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data="reject")
    ]])

    copied = await bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=keyboard
    )
    await message.answer("✅ Отправлено на модерацию!")

@dp.callback_query(F.data.in_(["approve", "reject"]))
async def moderation(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    if callback.data == "approve":
        await bot.copy_message(
            chat_id=CHANNEL,
            from_chat_id=ADMIN_ID,
            message_id=callback.message.message_id
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Опубликовано!")
    else:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Отклонено!")

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
