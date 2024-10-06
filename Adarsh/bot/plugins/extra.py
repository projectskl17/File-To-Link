from Adarsh.bot import StreamBot
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
import time
import shutil, psutil
from utils_bot import *
from Adarsh import StartTime

@StreamBot.on_message(filters.regex("ping"))
async def ping(bot, message):
    start_time = time.time()
    temp_message = await message.reply_text("....")
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    await temp_message.edit(f"Pong!\n{time_taken_ms:.3f} ms")

@StreamBot.on_message(filters.private & filters.regex("status"))
async def status(bot, message):
    current_time = readable_time((time.time() - StartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    bot_stats = f"""<b>Bot Uptime:</b> {current_time}
<b>Total Disk Space:</b> {total}
<b>Used:</b> {used}
<b>Free:</b> {free}

<b>Data Usage:</b>
<b>Upload:</b> {sent}
<b>Download:</b> {recv}

<b>CPU Usage:</b> {cpu_usage}% 
<b>RAM Usage:</b> {memory}% 
<b>Disk Usage:</b> {disk}%
"""
    await message.reply_text(bot_stats)
