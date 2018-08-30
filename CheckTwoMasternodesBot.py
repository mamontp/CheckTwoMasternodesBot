#!/usr/bin/python3
# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ParseMode
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, MessageHandler,
                          Filters, RegexHandler, ConversationHandler)
from emoji import emojize
import logging
from SQLighter import SQLighter
import requests
from datetime import datetime

# loging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# we initiate possible states
MAIN_MENU, ADD_COIN, ADD_ADDRESS, DELETE_ADDRESS = range(4)

coin = 'None'
database_name = 'users_address.db'

# set pictures and text for the main menu buttons
# all available pictures can be viewed here https://www.webfx.com/tools/emoji-cheat-sheet/
button_addres = emojize(':mailbox: Show coin address', use_aliases=True)
button_add  = emojize(':floppy_disk: Add address')
button_help = emojize(':mobile_phone: Help')
button_balance = emojize(':dollar: Balance', use_aliases=True)
button_delete = emojize(':bomb: Delete address')
button_status = emojize(':bank: Masternodes status')
button_donate = emojize(':cookie: Donate')

# create the main menu
reply_keyboard = [[button_status, button_balance, button_addres], [button_add, button_delete, button_help, button_donate]]
main_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Create a keyboard of coins.
coin_keyboard = [['vivo', 'gbx', 'pac', 'dev'], ['smart', 'bitg', 'pivx', 'xzc'], ['cancel']]
coin_markup = ReplyKeyboardMarkup(coin_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Create a keyboard of cancel.
cancel_keyboard = [['cancel']]
cancel_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True, resize_keyboard=True)

db_worker = SQLighter(database_name)

# If there is no table, then we create it.
db_worker.create_tabl()
db_worker.close()

# command method "/start"
def start(bot, update):
    update.message.reply_text(
        "The bot is used for the 2masternodes.com service. The bot checks the status of the node at the wallet address from which the coins were sent to the node.\n"
        "If the bot does not respond, enter /start or done and then /start.\n"
        "/start - start bot\n"
        "help - help\n"
        "add - add address\n"
        "delete - delete address\n"
        "status - status master nodes\n"
        "address - show coin address\n"
        "balance - show balance for address ",
        reply_markup=main_markup)
    return MAIN_MENU

# Help
def help(bot, update):
    update.message.reply_text(
        "If the bot does not respond, enter /start or done and then /start.\n"
        "/start - start bot\n"
        "help - help\n"
        "add - add address\n"
        "delete - delete address\n"
        "status - status master nodes\n"
        "address - show coin address\n"
        "balance - show balabce for address",
        reply_markup=main_markup)
    return MAIN_MENU

# method maim menu
def main_menu(bot, update):
    # get the text entered by the user in the chat
    # in fact it's text on the main menu buttons
    button_text = update.message.text
    # we check if there is a function in the list of functions, otherwise we return an error
    if button_text in button_func:
        return button_func[button_text](bot, update)
    else:
        update.message.reply_text('There is no such function.', reply_markup=main_markup)
    return MAIN_MENU

# Extracting from the database records corresponding to the specified chat_id.
# Data is transferred in the form of a two-dimensional array.
def get_address(chat_id):
    db_worker = SQLighter(database_name)
    AddressFromDB = db_worker.select_chat_id(chat_id)
    db_worker.close()
    return AddressFromDB

# send coin and address for a specific chat_id      coin - address
def send_addres(bot, update):
    chat_id = update.message.chat_id
    data = get_address(chat_id) # Data from DB
    if not data:
        bot.send_message(chat_id=update.message.chat_id, text='You do not have any addresses. Add address please.', reply_markup=main_markup)
    else:
        for row in data:
            string = row[1] + " - " + row[2]
            bot.send_message(chat_id=update.message.chat_id, text=string, reply_markup=main_markup)
    return MAIN_MENU

# Invitation to choose a coin
def add(bot, update):
    update.message.reply_text('We add a coin and an address.\nPlease choose a coin', reply_markup=coin_markup)
    return ADD_COIN

# dialog for adding a coin
def add_coin(bot, update):
    available_coins = {'xzc', 'gbx', 'pac', 'dev', 'smart', 'bitg', 'vivo', 'pivx'}
    global coin
    coin = update.message.text
    if coin == 'cancel':
        update.message.reply_text('Cancel', reply_markup=main_markup)
        return MAIN_MENU
    else:
        if coin in available_coins:
            update.message.reply_text('Enter the address of the wallet from which you made an investment in the node', reply_markup=cancel_markup)
            return ADD_ADDRESS
        else:
            update.message.reply_text('Unavailable coin.\nPlease choose a coin from the available.', reply_markup=coin_markup)
            return ADD_COIN

# dialog for adding a address
def add_addres(bot, update):
    chat_id = update.message.chat_id
    address = update.message.text

    if address == 'cancel':
        update.message.reply_text('Cancel', reply_markup=main_markup)
        return MAIN_MENU
    else:
        answer = str(balance(coin, address))
        if 'Error' in answer or 'not found' in answer:
            string = 'The address ***' + address + '*** can not be found in the explorer for the coin ***' + coin + '***\nEnter the address of the wallet'
            bot.send_message(chat_id=update.message.chat_id, text=string, parse_mode='MARKDOWN')
            return ADD_ADDRESS
        else:
            update.message.reply_text('Added coin ***' + coin +'*** with address ***' + address + '***', parse_mode='MARKDOWN', reply_markup=main_markup)

            # Add to DB
            db_worker = SQLighter(database_name)
            db_worker.add_address(chat_id, coin, address)
            db_worker.close()
            return MAIN_MENU

# function of getting a balance from the coin explorer
def balance(coin, address):
    url = {'gbx': 'https://explorer.gobyte.network/ext/getbalance/',
           'vivo': 'http://vivo.explorerz.top:3003/ext/getbalance/',
           'pac': 'http://usa.pacblockexplorer.com:3002/ext/getbalance/',
           'bitg': 'https://explorer.savebitcoin.io/ext/getbalance/',
           'dev': 'http://explorer.deviantcoin.io/ext/getbalance/',
           'xzc': 'https://xzc.ccore.online/ext/getbalance/',
           'smart': 'https://insight.smartcash.cc/api/addr/',
           'pivx': 'https://chainz.cryptoid.info/pivx/api.dws?q=getbalance&a='}
    if coin in url:
        try:
            parsed_string = requests.get(url[coin]+ address)
            if 'error' in parsed_string.text or 'Invalid' in parsed_string.text or 'invalid' in parsed_string.text or 'Error' in parsed_string.text:
                string = '***' + address + '*** not found in explorer'
                return string
            else:
                if coin == "smart":
                    return parsed_string.json()["balance"]
                else:
                    return parsed_string.text
        except requests.exceptions.HTTPError:
            print ("Http Error on explorer")
        except requests.exceptions.ConnectionError:
            print ("Error Connecting to explorer")
        except requests.exceptions.Timeout:
            print ("Timeout Error on explorer")
        except requests.exceptions.RequestException:
            print ("OOps: Something Error")

# Send balance to chat
def send_balance(bot, update):
    chat_id = update.message.chat_id
    data = get_address(chat_id) # Data from DB
    if not data:
        bot.send_message(chat_id=update.message.chat_id, text='You do not have any addresses. Add address please.', reply_markup=main_markup)
    else:
        for address in data:
            string = address[1] + " - " + str(balance(address[1],address[2]))
            bot.send_message(chat_id=update.message.chat_id, text=string, parse_mode='MARKDOWN', reply_markup=main_markup)
    return MAIN_MENU

# Invitation to choose a coin
def delete(bot, update):
    update.message.reply_text('We delete a coin and an address.\nAddresses available for deletion:', reply_markup=cancel_markup)
    # output a list of addresses that can be deleted
    chat_id = update.message.chat_id
    for row in get_address(chat_id):
        string = row[1] + " - " + row[2]
        bot.send_message(chat_id=update.message.chat_id, text=string, reply_markup=main_markup)

    update.message.reply_text('***Please enter a coin and address***\nThe string must be of the form:\n`coin - address`', parse_mode='MARKDOWN', reply_markup=cancel_markup)
    return DELETE_ADDRESS

# function of removing the address from the database
def delete_address(bot, update):
    chat_id = update.message.chat_id
    coin_address = update.message.text
    if coin_address == 'cancel':
        update.message.reply_text('Cancel', reply_markup=main_markup)
        return MAIN_MENU
    else:
        try:
            split_string = coin_address.split()     # Separation of the received line
            coin = split_string[0]
            address = split_string[2]
            # Delete from DB
            db_worker = SQLighter(database_name)
            answer = db_worker.delete_row(chat_id, coin, address)
            db_worker.close()
            update.message.reply_text(answer, reply_markup=main_markup)
            return MAIN_MENU
        except:
            update.message.reply_text('Invalid input format. The string format should be:\n`coin - address`', parse_mode='MARKDOWN', reply_markup=cancel_markup)
            return DELETE_ADDRESS

# function of receiving data from the site api.2masternodes.com/api/address for a given address.
def check_2masternodes(address):
    try:
        parsed_string = requests.get('http://api.2masternodes.com/api/address/'+ address)
        if 'error' in parsed_string.text or 'Invalid' in parsed_string.text or 'invalid' in parsed_string.text or 'Error' in parsed_string.text or 'ot Found' in parsed_string.text:
            string = '***' + address + '*** not found in 2masternodes.com'
            return string
        else:
            return parsed_string
    except requests.exceptions.HTTPError:
        print ("Http Error on explorer")
    except requests.exceptions.ConnectionError:
        print ("Error Connecting to explorer")
    except requests.exceptions.Timeout:
        print ("Timeout Error on explorer")
    except requests.exceptions.RequestException:
        print ("OOps: Something Error")

# output status masternode to all addresses
def status(bot, update):
    chat_id = update.message.chat_id
    data = get_address(chat_id) # Data from DB
    if not data:
        bot.send_message(chat_id=update.message.chat_id, text='You do not have any addresses. Add address please.', reply_markup=main_markup)
    else:
        for row in data:
            parsed_string = check_2masternodes(row[2])
            if 'Error' in parsed_string or 'not found' in parsed_string:
                bot.send_message(chat_id=update.message.chat_id, text=parsed_string, parse_mode='MARKDOWN', reply_markup=main_markup)
            else:
                json_string = parsed_string.json()
                coin = json_string["coin"]

                for b in json_string["beneficiary"]:
                    sum_royalty = 0
                    paidAt = "None"
                    masternode = b["masternode"]

                    strStatus = b["strStatus"]
                    if strStatus == "running":
                        Status = strStatus + emojize(":white_check_mark:", use_aliases=True)
                    else:
                        Status = strStatus + emojize(":x:", use_aliases=True)

                    amount = b["amount"]
                    for r in b["royalty"]:
                        if sum_royalty == 0:
                            paidAt = r["paidAt"]
                            if not (paidAt is None):
                                paidAt = datetime.strptime(paidAt, '%Y-%m-%dT%H:%M:%S.%fZ')
                        sum_royalty = sum_royalty + r["amount"]

                    string = "***" + coin + "*** " + masternode + " " + Status + "\namount - ***" + str(amount) + "***\nsum royalty - ***" \
                             + str(sum_royalty) + "***\nlast paid - ***" + str(paidAt) + "***\n"
                    bot.sendMessage(chat_id=update.message.chat_id, text=string, parse_mode='MARKDOWN', reply_markup=main_markup)
    return MAIN_MENU

def donate(bot, update):
    update.message.reply_text(
        "I would be grateful to the donations.\n"
        "***BTC*** - 128QgnZ2DwsFBssJdhrULCpMAuJqufp7pF\n"
        "***ETC*** - 0xf1d1dc2e0c927B69C69886c2D38B980E0C864251\n"
        "***GBX*** - GeWTh4Gg2mBzEsocGE3cVfpcrNdyyGPbnL\n"
        "***VIVO*** - VPPSGt1jwU8GnGpDA4hqFsk8pwj9V7Rsw4\n"
        "***BITG*** - ﻿GbnuPAiKPqo49okkddPWydeKqoRPHiVpNf\n"
        "***$PAC*** - PW2vv24GW3AXk9ZTqcPiqg9oFN86ZuL7by\n"
        "***Zcoin*** - aJsbGct8BWgS6nGHL3Bzz938TAzrhe1KYB\n"
        "***DEV*** - ﻿dYSs22C1dyqyXf46r5X6bNXYVrvaMFxfqW",
        parse_mode='MARKDOWN', reply_markup=main_markup)
    return MAIN_MENU

# method of completing the dialogue
def done(bot, update):
    user_data.clear()
    return ConversationHandler.END

# error method
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

# getting a token from a file
with open(r"token.txt", "r") as file:
        token = [row.strip() for row in file]

# create an update and pass them our token, which was issued after the creation of the bot
updater = Updater(token[0])

# define the called functions for the main menu buttons
button_func = {button_addres: send_addres, button_add: add, button_help: help, button_balance: send_balance, button_delete: delete, button_status: status, button_donate: donate}

# Prepare a list of possible choices for the main menu
main_menu_regexp = '|'.join([button_addres, button_add, button_help, button_balance, button_delete, button_status, button_donate])

# Initiate the handlers for the dialog
conversation = ConversationHandler(
    # command
    entry_points=[CommandHandler('start', start)],

    # state, depending on the state, the handler is called
    # The states are also transmitted by the already terminated handlers
    states={
        MAIN_MENU    : [RegexHandler('^(' + main_menu_regexp + ')$', main_menu)],
        ADD_COIN: [MessageHandler(Filters.text, add_coin)],
        ADD_ADDRESS: [MessageHandler(Filters.text, add_addres)],
        DELETE_ADDRESS: [MessageHandler(Filters.text, delete_address)]
    },

    fallbacks=[RegexHandler('^done$', done)]
)

# add state handlers to the dialog
updater.dispatcher.add_handler(conversation)

# error logging
updater.dispatcher.add_error_handler(error)

# launching the bot
updater.start_polling()

# start a wait loop
updater.idle()