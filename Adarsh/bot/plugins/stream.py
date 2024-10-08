#(c) Adarsh-Goel
import os
import asyncio
from asyncio import TimeoutError
from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus

from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
db = Database(Var.DATABASE_URL, Var.name)

MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

# New variables
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", None)
ADMINS = list(map(int, os.environ.get("ADMINS", "").split()))

# New function for subscription check
async def is_subscribed(filter, client, update):
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return False
    
    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

# Create the subscribed filter
subscribed = filters.create(is_subscribed)

@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo))
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
        )
    
    if not await is_subscribed(None, c, m):
        await handle_not_subscribed(c, m)
        return
    
    await process_file(c, m)

async def process_file(c: Client, m: Message):
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
       
        msg_text = """
<b>File Name:</b> <i>{}</i>
<b>File Size:</b> <i>{}</i>

<b>Download:</b> <i>{}</i>
<b>Watch:</b> <i>{}</i>
"""

        await log_msg.reply_text(
            text=f"""\
**Requested by:** [{m.from_user.first_name}](tg://user?id={m.from_user.id})  
**User ID:** `{m.from_user.id}`  
**Stream Link:** {stream_link}
""",
            disable_web_page_preview=True,
            quote=True
        )

        await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m)), online_link, stream_link),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Stream", url=stream_link),
                                                InlineKeyboardButton("Download", url=online_link)]])
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True)

async def handle_not_subscribed(client, message):
    buttons = [
        [
            InlineKeyboardButton("Join Channel", url=f"https://t.me/hermitmd_official")
        ],
        [
            InlineKeyboardButton("Try Now", callback_data=f"try_now_{message.id}")
        ]
    ]
    text = "**Please join our channel to use this bot!**\n\nClick the button below to join, then click 'Try Now':"
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

@StreamBot.on_callback_query(filters.regex('^try_now_'))
async def try_now_callback(client: Client, callback_query: CallbackQuery):
    message_id = int(callback_query.data.split('_')[2])
    original_message = await client.get_messages(callback_query.message.chat.id, message_id)
    
    if await is_subscribed(None, client, callback_query):
        try:
            # Delete the message with "Join Channel" and "Try Now" buttons
            await callback_query.message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")
        
        await callback_query.answer("Great! You've joined the channel. Processing your file now.", show_alert=True)
        await process_file(client, original_message)
    else:
        await callback_query.answer("You haven't joined the channel yet. Please join and try again.", show_alert=True)


@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo)  & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        await log_msg.reply_text(
            text = f"""\
**Channel Name:** `{broadcast.chat.title}`  
**Channel ID:** `{broadcast.chat.id}`  
**Request URL:** {stream_link}
""",
            quote=True
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Stream", url=stream_link),
                     InlineKeyboardButton("Download", url=online_link)] 
                ]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"GOT FLOODWAIT OF {str(w.x)}s FROM {broadcast.chat.title}\n\n**CHANNEL ID:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#ERROR_TRACKEBACK:** `{e}`", disable_web_page_preview=True)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ:  **Give me edit permission in updates and bin Channel!{e}**")
