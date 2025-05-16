import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler, ContextTypes
)
from utils.youtube import search_youtube, get_download_options, download_video, progress_status
from utils.auth import is_admin
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

VIDEO_STORE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the YouTube Downloader Bot!")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    results = search_youtube(query)
    keyboard = [[InlineKeyboardButton(r["title"][:40], callback_data=r["url"])] for r in results]
    await update.message.reply_text("Top Results:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_video_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = query.data
    formats = get_download_options(url)

    keyboard = [
        [InlineKeyboardButton(f"{k}", callback_data=f"{url}|{v}")]
        for k, v in formats.items() if k in ["144p", "360p", "720p", "1080p"]
    ]
    await query.edit_message_text("Choose a quality:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_quality_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url, format_id = query.data.split("|")
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("Access denied. Subscribe to use this bot.")
        return

    file_path = f"{user_id}_{format_id}.mp4"
    await query.edit_message_text("Downloading started...")

    download_video(url, format_id, file_path)

    percent, speed = progress_status.get(file_path, ("100%", "N/A"))
    await query.edit_message_text(f"Download complete: {percent} at {speed}")
    await context.bot.send_video(chat_id=query.message.chat.id, video=open(file_path, "rb"))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/search [query] - Search YouTube")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle_video_select, pattern=r"^https://"))
    app.add_handler(CallbackQueryHandler(handle_quality_select, pattern=r"\|"))

    app.run_polling()

if __name__ == "__main__":
    main()