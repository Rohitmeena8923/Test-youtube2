
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

    context.user_data["video_url"] = url

    try:
        formats = get_download_options(url)
        if not formats:
            await query.edit_message_text("No downloadable formats found.")
            return

        quality_buttons = []
        for label in ["144p", "360p", "720p", "1080p"]:
            if label in formats:
                fmt = formats[label]
                quality_buttons.append(
                    [InlineKeyboardButton(label, callback_data=f"quality|{fmt}|{label}")]
                )

        await query.edit_message_text(
            "Choose download quality:",
            reply_markup=InlineKeyboardMarkup(quality_buttons)
        )
    except Exception as e:
        await query.edit_message_text(f"Error getting formats: {e}")


async def handle_quality_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("Access denied. Subscribe to use this bot.")
        return

    try:
        _, format_id, label = query.data.split("|")
        video_url = context.user_data.get("video_url")

        if not video_url:
            await query.edit_message_text("Session expired. Please search again.")
            return

        output_path = f"{user_id}_{label}.mp4"
        await query.edit_message_text("Downloading started...")

        download_video(video_url, format_id, output_path)

        await query.edit_message_text(f"Download complete: {label}")
        await context.bot.send_video(chat_id=query.message.chat.id, video=open(output_path, "rb"))

    except Exception as e:
        await query.edit_message_text(f"Download failed: {e}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/search [query] - Search YouTube")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle_video_select, pattern=r"^https://"))
    app.add_handler(CallbackQueryHandler(handle_quality_select, pattern=r"^quality\\|"))

    app.run_polling()


if __name__ == "__main__":
    main()