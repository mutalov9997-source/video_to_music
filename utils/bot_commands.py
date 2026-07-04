from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from data import ADMINS
from loader import bot


async def set_commands() -> None:
    commands = [
        BotCommand(
            command="start",
            description="Botni ishga tushirish 🟢"
        ),
        BotCommand(
            command="help",
            description="Yordam 📃"
        ),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    for admin in ADMINS:
        commands.append(
            BotCommand(
                command="check",
                description="Admin uchun ⚡"
            )
        )
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(chat_id=admin))
