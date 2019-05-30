#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Telegram bot for smart gardening.
    Use a file named "token" for the token.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
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
    msg = "Ciao!"
    bot.sendMessage(chat_id=update.message.chat_id, text=msg,
                    parse_mode=ParseMode.MARKDOWN)


def help(bot, update):
    """Send a message when the command /help is issued."""
    help_message = ("*Welcome to your Smart Garden bot!*\n\n"
    "You can perform the following actions:\n"
    "- '/status': Get info about your gardens\n"
    "- '/status id': Get ID info about your gardens\n")

    bot.sendMessage(chat_id=update.message.chat_id, text=help_message,
                    parse_mode=ParseMode.MARKDOWN)


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

def status(bot, update, args):
    """Gets information about all the sensors in the gardens and their status
    Connected/Disconnected, and sends a summary to the user.
    """

    param = " ".join(args)

    with open('conf.json', "r") as f:
        config = json.loads(f.read())
    url = config["catalogURL"]
    port = config["port"]
    string = "http://" + url + ":" + port
    dynamic = json.loads(requests.get(string + '/status').text)
    static = json.loads(requests.get(string + '/static').text)

    if param == 'id':
        for g in static["gardens"]:
            devices = []
            status = '🏡 ' + g["gardenID"] + '   (' + g["name"] + ')'
            for p in g["plants"]:
                status = status + ('\n\n    🌱 ' + p["plantID"] +
                                  '   (' + p["name"] + ')')

                for g2 in dynamic["gardens"]:
                    if g2["gardenID"] == g["gardenID"]:
                        break
                for p2 in g2["plants"]:
                    if p2["plantID"] == p["plantID"]:
                        break
                for d2 in p2["devices"]:
                    devices.append(d2["devID"])

                for d in p["devices"]:
                    if d["devID"] in devices:
                        status = status + ('\n        ✅️ ' + d["devID"] +
                                          '   (' + d["name"] + ')')
                    else:
                        status = status + ('\n        ❌ ' + d["devID"] +
                                          '   (' + d["name"] + ')')

                    devices.append(d["devID"])
            update.message.reply_text(status)

    else:
        for g in static["gardens"]:
            devices = []
            status = '🏡 ' + g["name"]
            for p in g["plants"]:
                status = status + '\n\n    🌱 ' + p["name"]

                for g2 in dynamic["gardens"]:
                    if g2["gardenID"] == g["gardenID"]:
                        break
                for p2 in g2["plants"]:
                    if p2["plantID"] == p["plantID"]:
                        break
                for d2 in p2["devices"]:
                    devices.append(d2["devID"])

                for d in p["devices"]:
                    if d["devID"] in devices:
                        status = status + '\n        ✅️ ' + d["name"]
                    else:
                        status = status + '\n        ❌ ' + d["name"]

                    devices.append(d["devID"])
            update.message.reply_text(status)


############################ Main ##############################################
def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    with open('conf.json', "r") as f:
        config = json.loads(f.read())
    url = config["catalogURL"]
    port = config["port"]
    string = "http://" + url + ":" + port + "/" + "api/telegramtoken"
    token = json.loads(requests.get(string).text)
    token = token["token"]

    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status, pass_args=True))
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
