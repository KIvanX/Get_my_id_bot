
import asyncio
import html
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart

with open("token.txt", "r") as file:
    TOKEN = file.read().strip()


bot = Bot(token=TOKEN)
dp = Dispatcher()


def format_message(message: dict) -> str:
    from_user = message.get("from_user", {})
    forward_from = message.get("forward_from", {})
    forward_origin = message.get("forward_origin", {})
    dt = datetime.fromtimestamp(message["date"]).strftime("%Y-%m-%d %H:%M:%S")

    msg_text = message.get("text", "(без текста)")
    if message.get("entities"):
        for e in message["entities"]:
            if e["type"] == "code":
                start = e["offset"]
                end = start + e["length"]
                code = msg_text[start:end]
                msg_text = msg_text.replace(code, f"`{code}`")

    is_premium = "✅" if from_user.get("is_premium") else "❌"

    lines = [
        "📨 <b>Сообщение</b>",
        f"├  <b>Message ID:</b> {message['message_id']}",
        f"├  <b>Дата:</b> {dt}",
        "",
        f"👤 <b>Отправитель:</b>",
        f"├ <b>ID:</b> <code>{from_user.get('id')}</code>",
        f"├ <b>Имя:</b> {html.escape(from_user.get('first_name', ''))} {html.escape(from_user.get('last_name', ''))}",
        f"├ <b>Username:</b> @{from_user.get('username')}" if from_user.get('username') else "├ <b>Username:</b> —",
        f"├ <b>Премиум:</b> {is_premium}"
    ]

    if forward_from:
        lines.append("")
        lines.append("🔁 <b>Переслано от:</b>")
        lines.append(f"├ <b>ID:</b> <code>{forward_from.get('id')}</code>"),
        lines.append(f"├ <b>Имя:</b> {html.escape(forward_from.get('first_name', ''))}")

        if forward_from.get('username'):
            lines.append(f"├ <b>Username:</b> @{forward_from.get('username')}")

        if forward_from.get('is_premium'):
            lines.append(f"├ <b>Премиум:</b> {'✅' if forward_from.get('is_premium') else '❌'}")

    elif forward_origin:
        lines.append("")
        lines.append("🔁 <b>Переслано от:</b>")
        origin_type = forward_origin.get("type")

        if origin_type == "user":
            sender = forward_origin.get("sender_user", {})
            lines.append(f"├ <b>ID:</b> <code>{sender.get('id')}</code>")
            lines.append(f"├ <b>Имя:</b> {html.escape(sender.get('first_name', ''))} "
                         f"{html.escape(sender.get('last_name', ''))}")

            if sender.get('username'):
                lines.append(f"├ <b>Username:</b> @{sender.get('username')}")

            if sender.get('is_premium'):
                lines.append(f"├ <b>Премиум:</b> {'✅' if sender.get('is_premium') else '❌'}")

        elif origin_type == "channel":
            channel = forward_origin.get("chat", {})
            lines.append(f"├ <b>ID:</b> <code>{channel.get('id')}</code>")
            lines.append(f"├ <b>Канал:</b> {channel.get('title', '(без названия)')}")

            if channel.get('username'):
                lines.append(f"├ <b>Username:</b> @{channel['username']}")

            author_signature = forward_origin.get("author_signature")
            if author_signature:
                lines.append(f"├ <b>Автор:</b> {author_signature}")

        elif origin_type == "chat":
            channel = forward_origin.get("sender_chat", {})
            lines.append(f"├ <b>ID:</b> <code>{channel.get('id')}</code>")
            lines.append(f"├ <b>Группа:</b> {channel.get('title', '(без названия)')}")

            if channel.get('username'):
                lines.append(f"├ <b>Username:</b> @{channel['username']}")

            author_signature = forward_origin.get("author_signature")
            if author_signature:
                lines.append(f"├ <b>Автор:</b> {author_signature}")

    return "\n".join(lines)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    with open('users.txt') as f:
        users = f.read()[:-1].split('\n')

    if str(message.chat.id) not in users:
        with open('users.txt', 'a') as f:
            f.write(f"{message.chat.id}\n")

    text = (f"Привет, <b>{html.escape(message.from_user.full_name)}</b>!\n\n"
            f"Твой Telegram ID: <code>{message.from_user.id}</code>")

    if message.chat.id == 1914011859:
        text += f'\n\n👥 Количество пользователей: <b>{len(users)}</b>'

    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.text == "ping")
async def ping(message: Message):
    await message.answer("<b>PONG</b>", parse_mode=ParseMode.HTML)


@dp.message()
async def message_info(message: Message):
    info = format_message(message.model_dump())
    await message.answer(info, parse_mode=ParseMode.HTML)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
