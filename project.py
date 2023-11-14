from currency_converter import CurrencyConverter
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os

load_dotenv()

c = CurrencyConverter()
TOKEN: Final = os.environ.get('TELEGRAM_TOKEN')
BOT_USERNAME: Final = os.environ.get('BOT_NAME')
SELECT_AMOUNT = 0
SELECT_SOURCE_CURRENCY = 1
SELECT_TARGET_CURRENCY = 2

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! thanks for chatting with me! I am your servant!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please insert the amount of money you want to convert.')
    return SELECT_AMOUNT

async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = float(update.message.text)
    await update.message.reply_text('Now, please enter the source currency code (e.g., USD):')
    return SELECT_SOURCE_CURRENCY

async def receive_source_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['source_currency'] = update.message.text.upper()
    await update.message.reply_text('Great! Now, please enter the target currency code (e.g., EUR):')
    return SELECT_TARGET_CURRENCY

async def receive_target_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_currency = update.message.text.upper()
    amount = context.user_data['amount']
    source_currency = context.user_data['source_currency']
    converted_amount = c.convert(amount, source_currency, target_currency)
    converted_amount = round(converted_amount, 2)
    await update.message.reply_text(f'The converted amount from {source_currency} to {target_currency} is: {converted_amount}')

    return ConversationHandler.END


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def handler_response(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed:
        return 'I am good!'
    
    return ' I do not understand hehehe'

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Conversation handler
    custom_handler = ConversationHandler(
        entry_points=[CommandHandler('custom', custom_command)],
        states={
            SELECT_AMOUNT: [MessageHandler(filters.TEXT, receive_amount)],
            SELECT_SOURCE_CURRENCY: [MessageHandler(filters.TEXT, receive_source_currency)],
            SELECT_TARGET_CURRENCY: [MessageHandler(filters.TEXT, receive_target_currency)]
        },
        fallbacks=[]
    )
    
    # Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(custom_handler)

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
