from telegram.ext import JobQueue
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import add_vip, remove_vip, is_vip, get_expired_users

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GROUP_ID = int(os.getenv("GROUP_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_vip(update.effective_user.id):
        await update.message.reply_text("🔥 VIP aktif")
    else:
        await update.message.reply_text("❌ Bukan VIP")

async def addvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        days = int(context.args[1])
        add_vip(user_id, days)
        await update.message.reply_text("✅ VIP ditambahkan")
    except:
        await update.message.reply_text("Format: /addvip USER_ID HARI")

async def delvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    user_id = int(context.args[0])
    remove_vip(user_id)
    await update.message.reply_text("❌ VIP dihapus")

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_vip(update.effective_user.id):
        await update.message.reply_text("🔥 VIP aktif")
    else:
        await update.message.reply_text("🚫 Tidak VIP")

async def check_expired(context: ContextTypes.DEFAULT_TYPE):
    users = get_expired_users()
    for user in users:
        try:
            await context.bot.ban_chat_member(GROUP_ID, user[0])
            await context.bot.unban_chat_member(GROUP_ID, user[0])
            remove_vip(user[0])
        except:
            pass

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addvip", addvip))
app.add_handler(CommandHandler("delvip", delvip))
app.add_handler(CommandHandler("vip", vip))

app.job_queue.run_repeating(check_expired, interval=3600, first=10)

app.run_polling()
