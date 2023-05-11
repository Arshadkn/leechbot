import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, ADMIN, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
import re
import json
import base64
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('ʀᴇqᴜᴇꜱᴛ ɢʀᴏᴜᴩ', url='https://t.me/CinimaBranthen')
            ],
            [
                InlineKeyboardButton('#Pattisho:WTF || C0B', url=f"https://t.me/COBLINKS "),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('ᴄʟɪᴄᴋ ʜᴇʀᴇ ꜰᴏʀ ᴍᴏʀᴇ ʙᴜᴛᴛᴏɴs', callback_data='help')
           ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn = [[InlineKeyboardButton("ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=invite_link.invite_link),
                        InlineKeyboardButton("ᴍᴇ ᴊᴏɪɴᴇᴅ", callback_data=f"{pre}#{file_id}")],[
                        InlineKeyboardButton("Hᴇʏ Bᴏᴛ....! Wʜʏ I'ᴍ ᴊᴏɪɴɪɴɢ", callback_data="neosub")]]
            except (IndexError, ValueError):
                btn = [[InlineKeyboardButton("ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=invite_link.invite_link),
                        InlineKeyboardButton("ᴍᴇ ᴊᴏɪɴᴇᴅ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")],[
                        InlineKeyboardButton("Hᴇʏ Bᴏᴛ....! Wʜʏ I'ᴍ ᴊᴏɪɴɪɴɢ", callback_data="neosub")]]
        await client.send_message(
            chat_id=message.from_user.id,
            text="<b>⚠️ ᴘʟᴇᴀsᴇ ғᴏʟʟᴏᴡ ᴛʜɪs ʀᴜʟᴇs ⚠️</b>\n\n<b>{} ആദ്യം【 <a href=https://t.me/CblinkzZ>ᴊᴏɪɴ ɢʀᴏᴜᴘ</a> 】എന്ന ബട്ടൺ ക്ലിക്ക് ചെയ്തു ഗ്രൂപ്പിൽ ജോയിൻ ചെയ്.. എന്നിട്ട് വീണ്ടു ബോട്ടിൽ വന്നിട്ട്【 <a href=https://t.me/GxHeisenBot>ᴍᴇ ᴊᴏɪɴᴇᴅ</a> 】എന്ന ബട്ടൺ ക്ലിക്ക് ചെയ്താൽ ഫയൽ കിട്ടുന്നതായിരിക്കും</b>\n\n<b>Fɪʀsᴛ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ【 <a href=https://t.me/CblinkzZ>ᴊᴏɪɴ ɢʀᴏᴜᴘ</a> 】ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴛʜᴇɴ ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏ ᴛʜᴇ ʙᴏᴛ ᴄʟɪᴄᴋ ᴏɴ【 <a href=https://t.me/GxHeisenBot>ᴍᴇ ᴊᴏɪɴᴇᴅ</a> 】ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇ...</b>".format(message.from_user.mention),
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('ᴄʟɪᴄᴋ ʜᴇʀᴇ ꜰᴏʀ ᴍᴏʀᴇ ʙᴜᴛᴛᴏɴs', callback_data='help')
           ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            filetype = msg.media
            file = getattr(msg, filetype)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    buttons = [
                    [
                        InlineKeyboardButton('🚸 ᴅᴇʟᴇᴛᴇ', callback_data="close_pages"),
                        InlineKeyboardButton('💞 sʜᴀʀᴇ', url="https://t.me/share/url?url=**😱%20സിനിമ%20ഭ്രാന്തൻ.²·⁰%20😱%0A%0Aഏത്%20അർധരാത്രി%20ചോദിച്ചാലും%20പടം%20കിട്ടും,%20ലോകത്തിലെ%20ഒട്ടുമിക്ക%20ഭാഷകളിലുമുള്ള%20സിനിമകളുടെ%20കളക്ഷൻ..%20❤️%0A%0A👇%20GROUP%20LINK%20👇%0A@CinimaBranthen%0A@CinimaBranthen%0A@CinimaBranthen**")
                    ],
                    [
                        InlineKeyboardButton(text=f'🌿 Fɪʟᴇ sɪᴢᴇ 【 {size} 】🌿', callback_data='gxneo')
                    ]
                    ]
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        protect_content=True if pre == 'filep' else False
        )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')
        
@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('GTBERG.log')
    except Exception as e:
        await message.reply(str(e))
        
@Client.on_message(filters.command('submit') & filters.private)
async def report(bot, message):
        if message.reply_to_message:
                                  await bot.send_message(chat_id=ADMIN, text=f"<b>⭕️NEW MESSAGE⭕️\n \n🧿 Name: {message.from_user.mention}\n🧿 User ID:</b> <code>{message.chat.id}</code>")
                                  await bot.forward_messages(chat_id=ADMIN, from_chat_id=message.from_user.id, message_ids=message.reply_to_message.message_id)
                                  await message.reply_text("<b>✅ Your Feedback Successfully Submitted to the Admins</b>")
        else:
             await message.reply_text("<b>Use this command as the reply of any Message to Report</b>")

@Client.on_message(filters.command('reply') & filters.private)
async def replyt(bot, message):
    if message.from_user.id == ADMIN: 
               if message.reply_to_message:
                                    userid=int(message.text.replace("/reply"," "))
                                    await bot.send_message(chat_id=userid, text=f"<b>An Admin is responded to your feedback ✨</b>")
                                    await bot.copy_message(chat_id=userid, from_chat_id=ADMIN, message_id=message.reply_to_message.message_id)
                                    await message.reply_text("<b>✅ Your Reply Successfully Send to the User</b>")
               else:
                    await message.reply_text("<b>Use this command as the reply of any Message to Reply</b>")                         
    else:
         await message.reply_text("<b>That's not for you bruh 😅</b>")

@Client.on_message(filters.command('send') & filters.private)
async def send(bot, message):
    if message.from_user.id == ADMIN: 
               if message.reply_to_message:
                                    chatid=int(message.text.replace("/send"," "))
                                    await bot.copy_message(chat_id=chatid, from_chat_id=ADMIN, message_id=message.reply_to_message.message_id)
                                    await message.reply_text("<b>✅ Message Successfully Send to the Group</b>")
               else:
                    await message.reply_text("<b>Use this command as the reply of any Message to Send in Group</b>")                         
    else:
         await message.reply_text("<b>That's not for you bruh 😅</b>")

@Client.on_message(filters.command('pin') & filters.private)
async def pin(bot, message):
    if message.from_user.id == ADMIN: 
               if message.reply_to_message:
                                    chatid=int(message.text.replace("/pin"," "))
                                    p=await bot.copy_message(chat_id=chatid, from_chat_id=ADMIN, message_id=message.reply_to_message.message_id)
                                    await p.pin()
                                    await message.reply_text("<b>✅ Message Successfully Send to the Group And pinned</b>")
               else:
                    await message.reply_text("<b>Use this command as the reply of any Message to Send in Group</b>")                         
    else:
         await message.reply_text("<b>That's not for you bruh 😅</b>")
         
@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')

