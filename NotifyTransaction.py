#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Sending a notification that the service has sent the received coins to the user's address.

from SQLighter import SQLighter
import requests
import datetime
import logging
import configparser
import argparse, os


# loging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--path", "-p", type=str, required=True, help="The path on which the script is located")
args = parser.parse_args()

PWD = args.path + '/' if not args.path.endswith('/') else args.path   # working directory path
if not(os.path.isdir(PWD)):
    logger.error('The directory %s does not exist', PWD)
    exit()

database_name = PWD + 'users_address.db'    # database file name
if not(os.path.isfile(database_name)):
    logger.error('The file %s does not exist', database_name)
    exit()

# Record time to file
def write_last_time(time_now):
    try:
        with open(PWD + "LastCheckTime.txt", 'w') as f:
            f.write(str(time_now))
            logger.info('Time saved to file')
    except:
        logger.warning('Error saving time to file %s', PWD + "LastCheckTime.txt")
        exit()

# Reading time from file
def read_last_check_time():
    try:
        with open(PWD + "LastCheckTime.txt", 'r') as file:
            last_time = datetime.datetime.strptime([row.strip() for row in file][0], '%Y-%m-%d %H:%M:%S.%f')
            return last_time
    except:
        logger.warning('Error read file %s', PWD + "LastCheckTime.txt")
        exit()

# Extracting from the database all records.
# Data is transferred in the form of a two-dimensional array.
def get_address():
    db_worker = SQLighter(database_name)
    AddressFromDB = db_worker.select_all()
    db_worker.close()
    return AddressFromDB

# function of receiving data from the site api.2masternodes.com/api/address for a given address.
def check_2masternodes(address):
    url = 'http://api.2masternodes.com/api/address/'
    try:
        parsed_string = requests.get(url+ address)
        if 'error' in parsed_string.text or 'Invalid' in parsed_string.text or 'invalid' in parsed_string.text or 'Error' in parsed_string.text or 'ot Found' in parsed_string.text:
            logger.warning('Error "%s"', parsed_string.text + ' ' + url + address)
            string = 'Error ***' + address + '*** not found in 2masternodes.com'
            return string
        else:
            return parsed_string
    except requests.exceptions.HTTPError:
        logger.warning('Http Error on explorer "%s"', url+ address)
        return ("Http Error on explorer")
    except requests.exceptions.ConnectionError:
        logger.warning('Error Connecting to explorer "%s"', url+ address)
        return ("Error Connecting to explorer")
    except requests.exceptions.Timeout:
        logger.warning('Timeout Error on explorer "%s"', url+ address)
        return ("Timeout Error on explorer")
    except requests.exceptions.RequestException:
        logger.warning('OOps: Something Error "%s"', url+ address)
        return ("OOps: Something Error")

# Sending a message if paidAt is newer than the time of the last check (last_time).
def send_messages(last_time):
    data = get_address() # Data from DB
    if not data:
        logger.warning('You do not have any addresses. Add address please.')
    else:
        explorer_url = {'gbx': 'https://explorer.gobyte.network:5002/address/',
                        'vivo': 'https://chainz.cryptoid.info/vivo/search.dws?q=',
                        'pac': 'http://explorer.paccoin.net/address/', 			# 'http://usa.pacblockexplorer.com:3002/address/',
                        'bitg': 'https://www.coinexplorer.net/BITG/address/',
                        'dev': 'https://chainz.cryptoid.info/dev/search.dws?q=',
                        'xzc': 'https://chainz.cryptoid.info/xzc/search.dws?q=',
                        'smart': 'http://explorer3.smartcash.cc/address/',
                        'pivx': 'https://chainz.cryptoid.info/pivx/search.dws?q=',
                        'anon': 'https://explorer.anon.zeltrez.io/address/',
                        'mnp': 'https://explorer.mnpcoin.pro/address/',
                        'bwk': 'https://explorer.bulwarkcrypto.com/#/address/'}
        for row in data:
            if not row[1] == 'anon' and not row[1] == 'vivo' and not row[1] == 'smart':
                parsed_string = check_2masternodes(row[2])
                if not ('Error' in parsed_string) and not('not found' in parsed_string):
                    json_string = parsed_string.json()
                    coin = json_string["coin"]
                    for b in json_string["beneficiary"]:
                        paidAt = "None"
                        masternode = b["masternode"]

                        for r in b["royalty"]:
                            paidAt = r["paidAt"]
                            if not (paidAt is None):
                                paidAt = datetime.datetime.strptime(paidAt, '%Y-%m-%dT%H:%M:%S.%fZ')
                                if paidAt > last_time:
                                    link = explorer_url[coin] + str(row[2])
                                    bot_chatID = row[0]
                                    amount = r["amount"]
                                    text = '`' + masternode + '` send you [' + str(amount) + ' ' + str(coin).upper() + '](' + link +') at ' + str(paidAt) + ' UTC'
                                    #print(text)
                                    keys = {'chat_id': bot_chatID, 'parse_mode': 'Markdown', 'text': text, 'disable_web_page_preview': 'True'}
                                    url = 'https://api.telegram.org/bot' + token + '/sendMessage'
                                    requests.get(url, params=keys)

# error method
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

# getting a token from a config file
try:
    file = open(PWD + 'CheckTwoMasternodesBot.cfg')
except IOError as e:
    logger.warn('Not open the file %s', PWD + 'CheckTwoMasternodesBot.cfg')
    exit()
else:
    config = configparser.ConfigParser()
    config.read(PWD + 'CheckTwoMasternodesBot.cfg')

token = config['Global']['token']

time_now = datetime.datetime.utcnow() # The current time in the UTC time zone
logger.info('Script start time  %s', time_now)

last_time = read_last_check_time()  # Last run time read from file.
logger.info('Time in the file   %s', last_time)

send_messages(last_time)

write_last_time(time_now)   # Write start time to file
logger.info('Script stop time   %s', datetime.datetime.utcnow())
