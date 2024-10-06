from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Adarsh.bot import StreamBot
from Adarsh.vars import Var
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.database import Database
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = Database(Var.DATABASE_URL, Var.name)

@StreamBot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: New User [{message.from_user.first_name}](tg://user?id={user_id}) Started !!"
        )
    
    usr_cmd = message.text.split("_")[-1]
    if usr_cmd == "/start":
        await message.reply_text(
            text="""
I am a Telegram bot designed to generate permanent links for files and videos, as well as streaming links.

For assistance, please type /help.

Feel free to send me any video or file to explore my features!
            """,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Support", url="https://t.me/hermitmd_official")],
                [InlineKeyboardButton("Owner", url="https://t.me/a_dithya_n")]
            ])
        )
    else:
        try:
            file_id = int(usr_cmd)
            get_msg = await bot.get_messages(chat_id=Var.BIN_CHANNEL, message_ids=file_id)
            file_info = get_file_info(get_msg)
            
            stream_link = get_stream_link(file_id)
            
            msg_text = f"""Your link is generated...

File Name: {file_info['name']}
File Size: {file_info['size']}

Download Link: {stream_link}

This link is permanent and won't expire.
            """
            await message.reply_text(
                text=msg_text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Download Now", url=stream_link)]])
            )
        except Exception as e:
            logger.error(f"Error processing start command: {e}")
            await message.reply_text("An error occurred. Please try again later.")

@StreamBot.on_message(filters.command('help') & filters.private)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: New User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    
    help_text = """
Send me any file or video, and I will provide you with a permanent shareable link for it.

This link can be used to download or stream using external video players through my servers.

For streaming, simply copy the link and paste it into your video player to start streaming.

This bot also supports channels. Add me as an admin to your channel to get a real-time download link for every file or video posted.

For more information, type /about.
    """
    await message.reply_text(
        text=help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support", url="https://t.me/hermitmd_official")],
            [InlineKeyboardButton("Owner", url="https://t.me/a_dithya_n")]
        ])
    )

@StreamBot.on_message(filters.command('about') & filters.private)
async def about_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: New User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    
    about_text = """
Bot Name: HermiT File to Link
Support: [Hermit Official](https://t.me/hermitmd_official)
Server: VPS
Library: Pyrogram
Language: Python 3
    """
    await message.reply_text(
    text=about_text,
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Support", url="https://t.me/hermitmd_official")],
        [InlineKeyboardButton("Owner", url="https://t.me/a_dithya_n")]
    ])
    )

def get_file_info(message):
    if message.video:
        return {
            "size": humanbytes(message.video.file_size),
            "name": message.video.file_name
        }
    elif message.document:
        return {
            "size": humanbytes(message.document.file_size),
            "name": message.document.file_name
        }
    elif message.audio:
        return {
            "size": humanbytes(message.audio.file_size),
            "name": message.audio.file_name
        }
    return {"size": "N/A", "name": "N/A"}

def get_stream_link(file_id):
    if Var.ON_HEROKU or Var.NO_PORT:
        return f"https://{Var.FQDN}/{file_id}"
    else:
        return f"http://{Var.FQDN}:{Var.PORT}/{file_id}"

# Add error handling for the main bot loop
if __name__ == "__main__":
    try:
        StreamBot.run()
    except Exception as e:
        logger.error(f"Error in main bot loop: {e}")