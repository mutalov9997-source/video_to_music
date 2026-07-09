import os
import uuid
import asyncio
from loader import bot, dp, pyro
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, FSInputFile, CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.exceptions import TelegramBadRequest

from loader import bot, dp
from moviepy.editor import VideoFileClip

# ===== SETTINGS =====
DOWNLOAD_DIR = "downloads"
CHANNEL_USERNAME = "@prime_school_1"
CHANNEL_LINK = "https://t.me/prime_school_1"
SINGLE_VIDEO_STARS = 5
PREMIUM_STARS = 40
DONATE_OPTIONS = [1, 5, 10, 25]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

premium_users: set[int] = set()
single_credits: dict[int, int] = {}


# ===== USER STORAGE =====
def save_user(user_id: int):
    with open("users.txt", "a+") as f:
        f.seek(0)
        ids = f.read().splitlines()
        if str(user_id) not in ids:
            f.write(f"{user_id}\n")


def get_all_users() -> list[int]:
    try:
        with open("users.txt", "r") as f:
            return [int(i) for i in f.read().splitlines() if i]
    except FileNotFoundError:
        return []


async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False


def sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Subscribe to channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Check subscription", callback_data="check_sub")]
    ])


def payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎬 Convert 1 large video — {SINGLE_VIDEO_STARS} ⭐", callback_data="pay_single")],
        [InlineKeyboardButton(text=f"♾ Premium (unlimited) — {PREMIUM_STARS} ⭐", callback_data="pay_premium")],
        [InlineKeyboardButton(text="✊ Support us (donate)", callback_data="donate")]
    ])


def donate_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=f"⭐ {amount}", callback_data=f"donate_{amount}")
        for amount in DONATE_OPTIONS
    ]
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
    ])


@dp.message(CommandStart())
async def start_handler(message: Message):
    save_user(message.from_user.id)

    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "👋 Hello!\n\n"
            "🔒 To use this bot, please subscribe to our channel first:\n\n"
            f"👉 {CHANNEL_LINK}\n\n"
            "After subscribing, press ✅ Check subscription.",
            reply_markup=sub_keyboard()
        )
        return

    if message.from_user.id in premium_users:
        await message.answer(
            "👋 Welcome back!\n\n"
            "♾ You have <b>Premium</b> access — unlimited conversions!\n\n"
            "🎬 Send me a video and I will convert it to 🎵 MP3!"
        )
    else:
        await message.answer(
            "👋 Hello!\n\n"
            "🎬 Send me a video and I will convert it to 🎵 MP3!\n\n"
            "✅ Videos up to <b>20 MB</b> are <b>free!</b>\n\n"
            "For larger videos:\n"
            f"🎬 <b>1 large video</b> — {SINGLE_VIDEO_STARS} ⭐ Stars\n"
            f"♾ <b>Premium</b> (unlimited) — {PREMIUM_STARS} ⭐ Stars",
            reply_markup=payment_keyboard()
        )


@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)
    if not is_subscribed:
        await callback.answer("❌ You are not subscribed yet!", show_alert=True)
        return

    user_id = callback.from_user.id
    if user_id in premium_users:
        await callback.message.edit_text(
            "✅ Subscription confirmed!\n\n"
            "♾ You have <b>Premium</b> access!\n\n"
            "🎬 Send me a video and I will convert it to 🎵 MP3!"
        )
    else:
        await callback.message.edit_text(
            "✅ Subscription confirmed!\n\n"
            "🎬 Send me a video and I will convert it to 🎵 MP3!\n\n"
            "✅ Videos up to <b>20 MB</b> are <b>free!</b>\n\n"
            "For larger videos:\n"
            f"🎬 <b>1 large video</b> — {SINGLE_VIDEO_STARS} ⭐ Stars\n"
            f"♾ <b>Premium</b> (unlimited) — {PREMIUM_STARS} ⭐ Stars",
            reply_markup=payment_keyboard()
        )
    await callback.answer()


@dp.callback_query(F.data == "pay_single")
async def pay_single_callback(callback: CallbackQuery):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="🎬 1 Large Video Conversion",
        description="Convert 1 large video (20MB+) to MP3 with @Video_to_AudioBot",
        payload="single_video",
        currency="XTR",
        prices=[LabeledPrice(label="1 Large Video", amount=SINGLE_VIDEO_STARS)]
    )


@dp.callback_query(F.data == "pay_premium")
async def pay_premium_callback(callback: CallbackQuery):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="♾ Premium Access",
        description="Unlimited video to MP3 conversions with @Video_to_AudioBot",
        payload="premium_purchase",
        currency="XTR",
        prices=[LabeledPrice(label="Premium (unlimited)", amount=PREMIUM_STARS)]
    )


@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload

    if payload == "premium_purchase":
        premium_users.add(user_id)
        await message.answer(
            "🎉 Payment successful!\n\n"
            "♾ You now have <b>Premium</b> access — unlimited conversions!\n\n"
            "🎬 Send me a video and I will convert it to 🎵 MP3!"
        )
    elif payload == "single_video":
        single_credits[user_id] = single_credits.get(user_id, 0) + 1
        await message.answer(
            "🎉 Payment successful!\n\n"
            "🎬 You have <b>1 large video conversion</b> credit!\n\n"
            "Send me a large video now 👇"
        )
    elif payload == "donate":
        await message.answer(
            "💝 Thank you for your support!\n\n"
            "Your donation helps us keep the bot running! ✊"
        )


@dp.callback_query(F.data == "donate")
async def donate_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "💝 <b>Support us!</b>\n\n"
        "Your donation helps us keep the bot running.\n"
        "Choose the amount of Stars you'd like to send 👇",
        reply_markup=donate_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("donate_"))
async def donate_amount_callback(callback: CallbackQuery):
    amount = int(callback.data.split("_")[1])
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="💝 Support the bot",
        description=f"Donate {amount} ⭐ Stars to support @Video_to_AudioBot",
        payload="donate",
        currency="XTR",
        prices=[LabeledPrice(label=f"Donate {amount} Stars", amount=amount)]
    )


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "✅ Videos up to <b>20 MB</b> are <b>free!</b>\n\n"
        "For larger videos:\n"
        f"🎬 <b>1 large video</b> — {SINGLE_VIDEO_STARS} ⭐ Stars\n"
        f"♾ <b>Premium</b> (unlimited) — {PREMIUM_STARS} ⭐ Stars",
        reply_markup=payment_keyboard()
    )
    await callback.answer()


def convert_video_to_audio(video_path: str):
    audio_path = f"{uuid.uuid4().hex}.mp3"
    video_size = os.path.getsize(video_path)
    with VideoFileClip(video_path) as clip:
        clip.audio.write_audiofile(audio_path, logger=None)
    audio_size = os.path.getsize(audio_path)
    return audio_path, video_size, audio_size


@dp.message(F.video)
async def video_handler(message: Message):
    user_id = message.from_user.id

    is_subscribed = await check_subscription(user_id)
    if not is_subscribed:
        await message.answer(
            "❗ To use this bot, please subscribe to our channel first:\n\n"
            f"👉 {CHANNEL_LINK}",
            reply_markup=sub_keyboard()
        )
        return

    file_size = message.video.file_size
    is_large = file_size > 20 * 1024 * 1024

    # ✅ Admin uchun bepul
    from data.config import ADMINS
    is_admin = str(user_id) in ADMINS

    if is_large and not is_admin:
        is_premium = user_id in premium_users
        has_credit = single_credits.get(user_id, 0) > 0

        if not is_premium and not has_credit:
            await message.answer(
                f"⚠️ Your video is over 20 MB ({file_size / 1024 / 1024:.1f} MB)\n\n"
                "To convert large videos, choose an option:\n\n"
                f"🎬 <b>1 large video</b> — {SINGLE_VIDEO_STARS} ⭐ Stars\n"
                f"♾ <b>Premium</b> (unlimited) — {PREMIUM_STARS} ⭐ Stars",
                reply_markup=payment_keyboard()
            )
            return

        if not is_premium and has_credit:
            single_credits[user_id] -= 1

    wait_msg = await message.answer("⏳")

    file_id = message.video.file_id
    video_path = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4().hex}.mp4")

    if is_large:
        await wait_msg.edit_text("⏳ Downloading large file...")
        await pyro.connect()
        msg = await pyro.get_messages(message.chat.id, ids=message.message_id)
        downloaded = await pyro.download_media(msg, file=video_path)
        # downloaded — haqiqiy fayl yo'li
        video_path = downloaded  # haqiqiy yo'lni ishlatamiz

    audio_path = None
    try:
        audio_path, video_size, audio_size = convert_video_to_audio(video_path)

        await message.answer(
            f"📦 Video size: {video_size / 1024 / 1024:.2f} MB\n"
            f"🎵 Audio size: {audio_size / 1024 / 1024:.2f} MB"
        )

        await message.answer_audio(
            audio=FSInputFile(audio_path),
            title="🎧@Video_to_AudioBot",
            caption="@Video_to_AudioBot"
        )

    finally:
        await asyncio.sleep(1)
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except:
            pass
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass
        await wait_msg.delete()