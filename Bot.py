import os
import asyncio
import base64
import threading
import json
from datetime import datetime
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
app = Flask(__name__)
@app.route('/')
def home():
    return "Film4you Bot is Alive!"
def run_web():
    app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_web, daemon=True).start()
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]
MONGO_URI = os.environ.get("MONGO_URI")
FORCE_CHANNEL = "film4youofficial"
FORCE_CHANNEL_LINK = "https://t.me/film4youofficial"
OFFICIAL_FOOTER = "\n\n\n🔗 Main Channel: @film4youofficial\n🔍 Search Group: @moviesearchingg"
# ===== USERS PERSISTENT STORAGE - MongoDB + JSON Backup =====
TOTAL_USERS = set()
BROADCAST_MODE = set()
users_collection = None
try:
    if MONGO_URI:
        from pymongo import MongoClient
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = mongo_client["Film4YouBot"]
        users_collection = db["users"]
        for doc in users_collection.find({}, {"_id": 1}):
            TOTAL_USERS.add(doc["_id"])
        print(f"Loaded {len(TOTAL_USERS)} users from MongoDB")
except Exception as e:
    print(f"Mongo load error: {e}")
    users_collection = None
# JSON Backup (agar Mongo fail ho)
try:
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            for uid in json.load(f):
                TOTAL_USERS.add(int(uid))
except:
    pass
def save_user(user_id):
    try:
        TOTAL_USERS.add(user_id)
        if users_collection is not None:
            users_collection.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)
        with open("users.json", "w") as f:
            json.dump(list(TOTAL_USERS), f)
    except Exception as e:
        print(f"Save user error: {e}")
bot = Client("Film4youBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
async def auto_delete_message(chat_id, message_id):
    await asyncio.sleep(7200)
    try:
        await bot.delete_messages(chat_id, message_id)
    except:
        pass
async def is_joined(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        if member.status in ["kicked", "left"]:
            return False
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    is_admin = message.from_user.id in ADMINS
    if not is_admin:
        try:
            save_user(message.from_user.id)
            notify_text = f"""✨ Film4You | New User Joined
👤 User: {message.from_user.first_name}
💬 Username: @{message.from_user.username if message.from_user.username else 'No username'}
🆔 User ID: {message.from_user.id}
📊 Total Users: {len(TOTAL_USERS)}
⏰ Time: {datetime.now().strftime('%d %b, %I:%M %p')}"""
            for admin_id in ADMINS:
                try:
                    await client.send_message(admin_id, notify_text)
                except:
                    pass
        except:
            pass
    if not is_admin and not await is_joined(client, message.from_user.id):
        try:
            file_code = message.command[1] if len(message.command) > 1 else "0"
        except:
            file_code = "0"
        text = f"""🔰 Access Denied!
Hello {message.from_user.mention}!
You need to join our channel to get the file.
👇 Join channel and press Try Again"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel - Film4You Official", url=FORCE_CHANNEL_LINK)],
            [InlineKeyboardButton("🔄 Try Again", callback_data=f"try_{file_code}")]
        ])
        await message.reply(text=text, reply_markup=buttons)
        return
    if len(message.command) > 1:
        try:
            base64_string = message.command[1]
            base64_string += "=" * (-len(base64_string) % 4)
            decoded = base64.urlsafe_b64decode(base64_string).decode()
            file_id = int(decoded)
            msg = await client.get_messages(DB_CHANNEL, file_id)
            if not msg:
                await message.reply("❌ File not found!")
                return
            original_caption = msg.caption if msg.caption else ""
            new_caption = original_caption + OFFICIAL_FOOTER
            sent_msg = await msg.copy(message.chat.id, caption=new_caption)
            await message.reply("⚠️ File Auto-Delete Enabled\n\nThis file will be automatically deleted in 2 Hours to avoid copyright issues.\n📌 Please forward / save it to your Saved Messages.")
            asyncio.create_task(auto_delete_message(message.chat.id, sent_msg.id))
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        text = f"""👋 Hello {message.from_user.mention}!
🎬 Welcome to Film4You Player Bot
Get all the latest movies with direct links here. Just open any file link and enjoy.
💡 Want to request a movie? Join our group below!"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Main Channel", url="https://t.me/film4youofficial")],
            [InlineKeyboardButton("🎬 Join Request Group", url="https://t.me/moviesearchingg"), InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("❓ Help", callback_data="help"), InlineKeyboardButton("📞 Contact Us", url="https://t.me/iamsrm0")],
            [InlineKeyboardButton("🚀 Latest Updates", url="https://t.me/film4youofficial")]
        ])
        await message.reply(text=text, reply_markup=buttons, disable_web_page_preview=True)
# ===== ADMIN COMMANDS =====
@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    text = """❓ How to Use Film4You Bot
1. Join @film4youofficial
2. Click on the movie link
3. Bot will send you the file
4. Forward / Save file within 2 Hours

📢 Channel: @film4youofficial
🎬 Request Group: @moviesearchingg
📞 Contact Us: @iamsrm0"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Us", url="https://t.me/iamsrm0")],
        [InlineKeyboardButton("📢 Main Channel", url="https://t.me/film4youofficial")]
    ])
    await message.reply(text, reply_markup=buttons)
@bot.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def users_cmd(client, message):
    await message.reply(f"📊 Total Users: {len(TOTAL_USERS)}\n\n✅ Users are saved in Database - Will NOT reset on restart.")
@bot.on_message(filters.command("stats") & filters.private & filters.user(ADMINS))
async def stats_cmd(client, message):
    await message.reply(f"📊 Film4You Bot Stats\n\n👥 Total Users: {len(TOTAL_USERS)}\n🎬 Bot Status: ✅ Online\n⚙️ Version: 4.0\n📢 Channel: @film4youofficial\n📞 Owner: @iamsrm0")
@bot.on_message(filters.command("broadcast") & filters.private & filters.user(ADMINS))
async def broadcast_cmd(client, message):
    if len(message.command) > 1:
        broadcast_text = " ".join(message.command[1:])
        success = 0
        failed = 0
        status = await message.reply(f"📢 Broadcasting to {len(TOTAL_USERS)} users...")
        for user_id in list(TOTAL_USERS):
            try:
                await client.send_message(user_id, broadcast_text)
                success += 1
                await asyncio.sleep(0.05)
            except:
                failed += 1
        await status.edit_text(f"✅ Broadcast Completed!\n\n✔️ Success: {success}\n❌ Failed: {failed}")
        return
    BROADCAST_MODE.add(message.from_user.id)
    await message.reply("📢 Send your Broadcast Message now.\nSend any Text / Photo / Video - It will be sent to all users.\n\nTo cancel, send /cancel")
@bot.on_message(filters.command("cancel") & filters.private & filters.user(ADMINS))
async def cancel_cmd(client, message):
    BROADCAST_MODE.discard(message.from_user.id)
    await message.reply("❌ Broadcast Cancelled.")
# ===== FIXED: Broadcast Text Handler Only - No File Conflict =====
@bot.on_message(filters.private & filters.user(ADMINS) & filters.text & ~filters.command(["start", "help", "users", "stats", "broadcast", "cancel"]))
async def broadcast_text_handler(client, message):
    if message.from_user.id in BROADCAST_MODE:
        BROADCAST_MODE.discard(message.from_user.id)
        success = 0
        failed = 0
        status = await message.reply(f"📢 Broadcasting to {len(TOTAL_USERS)} users...")
        for user_id in list(TOTAL_USERS):
            try:
                await message.copy(user_id)
                success += 1
                await asyncio.sleep(0.05)
            except:
                failed += 1
        await status.edit_text(f"✅ Broadcast Completed!\n\n✔️ Success: {success}\n❌ Failed: {failed}")
        return
# ===== FIXED: Single File Handler - Broadcast + Link Generation =====
@bot.on_message(filters.private & filters.user(ADMINS) & (filters.document | filters.video | filters.audio | filters.photo))
async def save_and_gen_link(client, message):
    # If Broadcast Mode is ON, broadcast this file instead of generating link
    if message.from_user.id in BROADCAST_MODE:
        BROADCAST_MODE.discard(message.from_user.id)
        success = 0
        failed = 0
        status = await message.reply(f"📢 Broadcasting to {len(TOTAL_USERS)} users...")
        for user_id in list(TOTAL_USERS):
            try:
                await message.copy(user_id)
                success += 1
                await asyncio.sleep(0.05)
            except:
                failed += 1
        await status.edit_text(f"✅ Broadcast Completed!\n\n✔️ Success: {success}\n❌ Failed: {failed}")
        return
    try:
        sent = await message.copy(DB_CHANNEL, caption=message.caption if message.caption else "")
        file_id = sent.id
        string = str(file_id)
        b64 = base64.urlsafe_b64encode(string.encode()).decode().strip("=")
        bot_username = (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={b64}"
        await message.reply(f"✅ Link Generated!\n\n🔗 {link}\n\n📁 File saved to DB Channel.", disable_web_page_preview=True)
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
@bot.on_callback_query()
async def callbacks(client, query):
    if query.data == "about":
        text = """🎬 About Film4You Bot
👑 Owner: @iamsrm0
📢 Channel: @film4youofficial
📞 Contact Us: @iamsrm0
⚙️ Version: 4.0"""
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact Us", url="https://t.me/iamsrm0")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]))
    elif query.data == "help":
        text = """❓ How to Use?
1. Join @film4youofficial
2. Click on the movie link
3. Bot will send you the file

📞 Any Problem? Contact: @iamsrm0"""
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact Us", url="https://t.me/iamsrm0")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]))
    elif query.data == "back":
        text = f"""👋 Hello {query.from_user.mention}!
🎬 Welcome to Film4You Player Bot
Get all the latest movies with direct links here.
💡 Want to request a movie? Join our group below!"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Main Channel", url="https://t.me/film4youofficial")],
            [InlineKeyboardButton("🎬 Join Request Group", url="https://t.me/moviesearchingg"), InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("❓ Help", callback_data="help"), InlineKeyboardButton("📞 Contact Us", url="https://t.me/iamsrm0")],
            [InlineKeyboardButton("🚀 Latest Updates", url="https://t.me/film4youofficial")]
        ])
        await query.message.edit_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
    elif query.data.startswith("try_"):
        if not await is_joined(client, query.from_user.id):
            await query.answer("❌ Please join the channel first!", show_alert=True)
            return
        file_code = query.data.split("_", 1)[1]
        await query.message.delete()
        if file_code == "0":
            await query.message.reply(f"✅ Thanks for joining! You can now get movies {query.from_user.mention}")
        else:
            try:
                base64_string = file_code
                base64_string += "=" * (-len(base64_string) % 4)
                decoded = base64.urlsafe_b64decode(base64_string).decode()
                file_id = int(decoded)
                msg = await client.get_messages(DB_CHANNEL, file_id)
                original_caption = msg.caption if msg.caption else ""
                new_caption = original_caption + OFFICIAL_FOOTER
                sent_msg = await msg.copy(query.message.chat.id, caption=new_caption)
                await query.message.reply("⚠️ File Auto-Delete Enabled\n\nThis file will be automatically deleted in 2 Hours to avoid copyright issues.\n📌 Please forward / save it to your Saved Messages.")
                asyncio.create_task(auto_delete_message(query.message.chat.id, sent_msg.id))
            except Exception as e:
                await query.message.reply(f"❌ Error: {e}")
bot.run()
