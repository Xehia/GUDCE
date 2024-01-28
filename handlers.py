from telegram.ext import MessageHandler, Filters

# Echo message handler
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)