import psutil
import time
from pyrogram import filters, Client
from FileStream.bot import FileStream
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums.parse_mode import ParseMode
from FileStream.utils.bot_utils import verify_user
from FileStream.utils.time_format import get_readable_time
from FileStream.utils.human_readable import humanbytes

# Track uptime
start_time = time.time()

# ---------- Progress Bar ----------

def make_bar(p):
    filled = int(p / 10)
    return "▰" * filled + "▱" * (10 - filled)

# ---------- Build UI ----------

def build_usage_text():
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    inbound = humanbytes(net_io.bytes_recv)
    outbound = humanbytes(net_io.bytes_sent)

    uptime = int(time.time() - start_time)

    text = (
        "<b>╭━━━〔 ⚡ SYSTEM DASHBOARD ⚡ 〕━━━╮</b>\n\n"

        f"⏱ <b>Uptime:</b> <code>{get_readable_time(uptime)}</code>\n\n"

        "🖥️ <b>CPU Usage</b>\n"
        f"├ <code>{cpu_usage:.1f}%</code>\n"
        f"└ <code>{make_bar(cpu_usage)}</code>\n\n"

        "🧠 <b>Memory (RAM)</b>\n"
        f"├ <code>{ram.percent:.1f}%</code>\n"
        f"├ <code>{make_bar(ram.percent)}</code>\n"
        f"└ <i>{humanbytes(ram.used)} / {humanbytes(ram.total)}</i>\n\n"

        "💾 <b>Disk Storage</b>\n"
        f"├ <code>{disk.percent:.1f}% used</code>\n"
        f"└ <i>{humanbytes(disk.free)} free</i>\n\n"

        "🌐 <b>Network Traffic</b>\n"
        f"├ 📥 <b>Download:</b> <code>{inbound}</code>\n"
        f"└ 📤 <b>Upload:</b>   <code>{outbound}</code>\n\n"

        "<b>╰━━━〔 🚀 FSB MONITORING ACTIVE 〕━━━╯</b>"
    )

    return text

# ---------- Keyboard ----------

def usage_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="usage_refresh")
            ]
        ]
    )

# ---------- Command ----------

@FileStream.on_message(filters.command("usage") & filters.private)
async def usage_stats(bot: Client, message: Message):
    if not await verify_user(bot, message):
        return

    text = build_usage_text()

    await message.reply_text(
        text,
        reply_markup=usage_keyboard(),
        parse_mode=ParseMode.HTML
    )