import logging
from commands import *
from telegram.ext import ApplicationBuilder, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING)


if __name__ == '__main__':
    application = ApplicationBuilder().token('').build()

    # Add command handlers
    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(create_handler)

    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()