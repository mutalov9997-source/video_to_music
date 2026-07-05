from aiogram import F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup,
    LabeledPrice
)

from data.config import ADMINS
from handlers.users.start import premium_users
from loader import bot, dp
import asyncio

SUPPORT_STARS = 10  # Donate miqdori

def get_all_users() -> list[int]:
    try:
        with open("users.txt", "r") as f:
            return [int(i) for i in f.read().splitlines() if i]
    except FileNotFoundError:
        return []


def support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"⭐ Support us — {SUPPORT_STARS} Stars",
            callback_data="support_donate"
        )]
    ])


@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if str(message.from_user.id) not in ADMINS:
        return

    users = get_all_users()
    await message.answer(
        f"👨‍💼 <b>Admin Panel</b>\n\n"
        f"👥 Total users: {len(users)}\n\n"
        "Choose an action:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Send message to all", callback_data="broadcast")],
            [InlineKeyboardButton(text="📊 Statistics", callback_data="stats")]
        ])
    )


@dp.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    if str(callback.from_user.id) not in ADMINS:
        return

    users = get_all_users()
    await callback.message.edit_text(
        f"📊 <b>Statistics</b>\n\n"
        f"👥 Total users: {len(users)}\n"
        f"⭐ Premium users: {len(premium_users)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_back")]
        ])
    )
    await callback.answer()


@dp.callback_query(F.data == "admin_back")
async def admin_back_callback(callback: CallbackQuery):
    if str(callback.from_user.id) not in ADMINS:
        return

    users = get_all_users()
    await callback.message.edit_text(
        f"👨‍💼 <b>Admin Panel</b>\n\n"
        f"👥 Total users: {len(users)}\n\n"
        "Choose an action:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Send message to all", callback_data="broadcast")],
            [InlineKeyboardButton(text="📊 Statistics", callback_data="stats")]
        ])
    )
    await callback.answer()


# Broadcast — admin xabar yozadi
broadcast_data = {}

@dp.callback_query(F.data == "broadcast")
async def broadcast_callback(callback: CallbackQuery):
    if str(callback.from_user.id) not in ADMINS:
        return

    broadcast_data[callback.from_user.id] = True
    await callback.message.edit_text(
        "📢 <b>Send message to all users</b>\n\n"
        "Write your message below.\n"
        "You can send text, photo, or video.\n\n"
        "The message will have a <b>⭐ Support us</b> button.",
    )
    await callback.answer()


@dp.message(F.text | F.photo | F.video)
async def broadcast_message(message: Message):
    if str(message.from_user.id) not in ADMINS:
        return

    if not broadcast_data.get(message.from_user.id):
        return

    broadcast_data[message.from_user.id] = False

    users = get_all_users()
    sent = 0
    failed = 0

    status_msg = await message.answer(f"⏳ Sending to {len(users)} users...")

    for user_id in users:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or "",
                    reply_markup=support_keyboard()
                )
            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption or "",
                    reply_markup=support_keyboard()
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=message.text,
                    reply_markup=support_keyboard()
                )
            sent += 1
        except Exception:
            failed += 1

        await asyncio.sleep(0.05)  # Spam bo'lmasin

    await status_msg.edit_text(
        f"✅ <b>Done!</b>\n\n"
        f"📨 Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )


@dp.callback_query(F.data == "support_donate")
async def support_donate_callback(callback: CallbackQuery):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="⭐ Support the bot",
        description="Your support helps us keep the bot running! ❤️",
        payload="donate",
        currency="XTR",
        prices=[LabeledPrice(label="Support", amount=SUPPORT_STARS)]
    )