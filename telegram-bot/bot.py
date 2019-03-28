#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Telegram bot for smart gardening.
    Use a file named "token" for the token.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import logging
import json
import requests
import paho.mqtt.client as PahoMQTT


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Ciao!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('HELP!')


def echo(bot, update):
    """Echo the user message."""
    #update.message.reply_text(update.message.text)
    update.message.reply_text("Stai zitto!")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def irrigation(bot, update):
    update.message.reply_text("Avvio irrigazione...")
    update.message.reply_text("Irrigazione fallita!")
    # funzione...

def status(bot, update):
    update.message.reply_text("Magari metti qualche sensore")
    # funzione...

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    with open('token') as t:
        token = t.read().splitlines()[0]

    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("irrigate", irrigation))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
