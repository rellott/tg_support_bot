import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resend the user message to a Telegram channel."""
    message = update.message.text
    sender_name = update.effective_user.username
    if sender_name is None:
        sender_id = update.effective_user.id
        sender_full_name = update.effective_user.full_name
        text = f"id пользователя: {sender_id}\nИмя пользователя: {sender_full_name}\nСообщение: {message}"
    else:
        text = f"@{sender_name}: {message}"
    try:
        await context.bot.send_message(chat_id="-1001436167996", text=text)
        await update.message.reply_text("Message forwarded to channel!")
    except Exception as e:
        logger.error(f"Failed to send message. Error: {e}")
        await update.message.reply_text("Failed to forward message.")


async def send_to_user(update: Update, context: CallbackContext) -> None:
    """Send a message from a support team member to the user who sent the message."""
    # Check if the message was sent by a support team member in the channel
    if update.message.chat.type != "private":
        channel_member = await context.bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
        if channel_member.status == "member":
            logger.info("Unauthorized user attempted to send a message to user.")
            await update.message.reply_text("You are not authorized to send messages to users.")
            return

    # Check if the message is a reply to the user's message
    if not update.message.reply_to_message:
        logger.info("Message is not a reply to user's message.")
        await update.message.reply_text("Please reply to the user's message to send a message to them.")
        return

    message = update.message.text
    channel_name = update.effective_chat.username
    text = f"From {channel_name}: {message}"
    try:
        chat_id = update.message.reply_to_message.forward_from.id
        logger.info(chat_id)
        await context.bot.send_message(chat_id=chat_id, text=text)
        await update.message.reply_text("Message sent to user!")
    except Exception as e:
        logger.error(f"Failed to send message. Error: {e}")
        await update.message.reply_text("Failed to send message to user.")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5926456628:AAFASsarkVWpKk_NBrCizFzF-2uG3eCOey8").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("send", send_to_channel))
    application.add_handler(CommandHandler("send", send_to_user))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_to_channel))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
