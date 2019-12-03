#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Telegram bot for smart gardening."""

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import logging
import json
import requests
import time
import datetime
import paho.mqtt.client as PahoMQTT
import numpy as np

CHAT_ID = None  # For spot.

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class MyPublisher(object):
    def __init__(self, clientID, serverIP, port):
        self.clientID = clientID + '_pub'
        self.devID = clientID
        self.port = int(port)
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("P - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message, topic):
        print(json.dumps(json.loads(message), indent=2))
        self._paho_mqtt.publish(topic, message, 2)
        print("Publishing on %s:" % topic)


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
                    "- '/status id': Get ID info about your gardens\n"
                    "- '/plant id': Get info about your plants")

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

    with open('conf.json', "r") as f:
        config = json.loads(f.read())
    url = config["catalogURL"]
    port = config["port"]
    string = "http://" + url + ":" + port
    dynamic = json.loads(requests.get(string + '/dynamic').text)
    static = json.loads(requests.get(string + '/static').text)
    broker = json.loads(requests.get(string + '/broker').text)
    mqtt_port = broker["mqtt_port"]
    IP = broker["IP"]

    irrigation_list = []
    for g in static["gardens"]:
        for p in g["plants"]:
            for d in p["devices"]:
                for r in d["resources"]:
                    if r["n"].lower() == 'irrigation':
                        irrigation_list.append(d["devID"])

    pub = MyPublisher('bot', IP, mqtt_port)
    pub.start()

    while pub.loop_flag:
        print("Waiting for connection...")
        time.sleep(.01)

    print(irrigation_list)
    for d in irrigation_list:
        try:
            string = "http://" + url + ":" + port + "/info/" + d
            # print(string)
            r = json.loads(requests.get(string).text)
            topic = r["topic"]

            if topic == None:
                update.message.reply_text("❌ Irrigation FAILED on %s" % d)
            else:
                message = {
                           "e": [{
                             "n": "irrigate", "d": 120
                                }]
                           }

                message = json.dumps(message)
                pub.my_publish(message, topic)
                update.message.reply_text("💧 Irrigation started on %s" % d)
        except:
            print("Something gone wrong")

    pub.stop()

    # funzione...


def values(bot, update, args):
    """Get information about all sensor values for every plant."""
    # Read input.
    try:
        plantID = " ".join(args)
        if plantID[0:2] != 'p_':
            raise Exception

    except Exception:
        msg = "You must provide a `plantID`"
        bot.sendMessage(chat_id=update.message.chat_id, text=msg,
                        parse_mode=ParseMode.MARKDOWN)
        return

    # Read catalog URL and port from configuration file.
    with open('conf.json', "r") as f:
        config = json.loads(f.read())
    url = config["catalogURL"]
    port = config["port"]
    string = "http://" + url + ":" + port
    # dynamic = json.loads(requests.get(string + '/dynamic').text)
    static = json.loads(requests.get(string + '/static').text)
    # flag = 0

    ts = json.loads(requests.get(string + '/ts').text)
    ts_url, ts_port = ["http://" + ts["IP"], ts["port"]]
    # Find plantID on catalog.
    # try:
    #     r = json.loads(requests.get(string + '/info/' + plantID).text)
    #     thingspeakID = str(r["thingspeakID"])
    #     name = str(r["name"])

    # except Exception:
    #     msg = "You must provide a valid `plantID`"
    #     bot.sendMessage(chat_id=update.message.chat_id, text=msg,
    #                     parse_mode=ParseMode.MARKDOWN)
    #     return

    # Find resources associated to the plantID.
    time = "minutes"
    tval = "50"

    for g in static["gardens"]:
        if (update.message.from_user.username).lower() in g["users"]:

            for p in g["plants"]:
                if p["plantID"] == plantID:
                    now = datetime.datetime.now()
                    message = ('🌱 ' + p["name"] +
                               '\n    🕒' + ' ' + str(now.hour) + ':' +
                               str(now.minute))

                    for d in p["devices"]:

                        for res in d["resources"]:
                            string = (ts_url + ":" + ts_port + "/data/" +
                                      plantID + "/" + res["n"] + "?time=" +
                                      time + "&tval=" + tval + "&plantID=" +
                                      plantID + "&devID=" + d["devID"])
                            r = json.loads(requests.get(string).text)
                            data = r["data"]

                            if data != []:
                                m = np.mean(data)
                                message += ('\n    🔸' + res["n"].capitalize()
                                            + ': ' + str(m.round(2)) + ' ' +
                                            res["u"])

                            else:
                                message += ('\n    🔺' + res["n"].capitalize()
                                            + ': ' + str('n.a.'))

    message = message.replace('Celsius', '°C')
    update.message.reply_text(message)


def status(bot, update, args):
    """Get information about all the sensors n the gardens and their status
    Connected/Disconnected, and sends a summary to the user.
    """

    param = " ".join(args)

    with open('conf.json', "r") as f:
        config = json.loads(f.read())
    url = config["catalogURL"]
    port = config["port"]
    string = "http://" + url + ":" + port
    dynamic = json.loads(requests.get(string + '/dynamic').text)
    static = json.loads(requests.get(string + '/static').text)

    if param == 'id':

        for g in static["gardens"]:
            if (update.message.from_user.username).lower() in g["users"]:

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
                update.message.reply_text("You are not a user of this garden")


    else:
        for g in static["gardens"]:
            if update.message.from_user.username in g["users"]:
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
            else:
                pass

def chat(bot, update):
    global CHAT_ID
    CHAT_ID = update.message.chat_id

def spot(bot, update):
    msg = ("*Irrigation has started now!*\n"
            "⏱ 10 minutes\n"
            "🔸 Wind: 12 kn\n"
            "🔸 Humidity: 36 %\n"
            "🔸 Temperature: 24 ºC\n"
            "🔸 Rain: No")

    bot.sendMessage(chat_id=CHAT_ID,
                    text=msg, parse_mode=ParseMode.MARKDOWN)

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
    dp.add_handler(CommandHandler("values", values, pass_args=True))
    dp.add_handler(CommandHandler("irrigate", irrigation))
    dp.add_handler(CommandHandler("spot", spot))
    dp.add_handler(CommandHandler("chat", chat))

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
    spot()
