import psutil
import time
from pyrogram import filters, Client
from FileStream.bot import FileStream
from pyrogram.types import Message
from FileStream.utils.bot_utils import verify_user
from FileStream.utils.human_readable import humanbytes

# To track bandwidth delta
start_time = time.time()
last_stats = psutil.net_io_counters()

@FileStream.on_message(filters.command('usage') & filters.private)
async def usage_stats(bot: Client, message: Message):
    if not await verify_user(bot, message):
        return

    # CPU & RAM
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Bandwidth Calculation (Current Session)
    net_io = psutil.net_io_counters()
    inbound = humanbytes(net_io.bytes_recv)
    outbound = humanbytes(net_io.bytes_sent)

    # Simple Progress Bar Logic
    def make_bar(percentage):
        filled = int(percentage / 10)
        return "■" * filled + "□" * (10 - filled)

    usage_text = (
        "<b>╭━━━〔 🖥️ SYSTEM STATUS 〕━━━╼</b>\n"
        f"<b>┃</b>\n"
        f"<b>┃ ⚙️ CPU:</b> <code>{cpu_usage}%</code>\n"
        f"<b>┃</b> <code>[{make_bar(cpu_usage)}]</code>\n"
        f"<b>┃</b>\n"
        f"<b>┃ 🧠 RAM:</b> <code>{ram.percent}%</code>\n"
        f"<b>┃</b> <code>[{make_bar(ram.percent)}]</code>\n"
        f"<b>┃</b> <i>({humanbytes(ram.used)} / {humanbytes(ram.total)})</i>\n"
        f"<b>┃</b>\n"
        f"<b>┃ 📁 DISK:</b> <code>{disk.percent}%</code>\n"
        f"<b>┃</b> <i>({humanbytes(disk.free)} free)</i>\n"
        f"<b>┃</b>\n"
        f"<b>┃ 🌐 BANDWIDTH:</b>\n"
        f"<b>┃</b> 📥 <b>Inbound:</b> <code>{inbound}</code>\n"
        f"<b>┃</b> 📤 <b>Outbound:</b> <code>{outbound}</code>\n"
        f"<b>┃</b>\n"
        "<b>╰━━━━━━━━━━━━━━━━━━━━━━╼</b>"
    )

    await message.reply_text(usage_text, parse_mode=ParseMode.HTML)
