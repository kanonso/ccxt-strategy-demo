import ccxt
from datetime import datetime
import pandas as pd
import ccxt,configparser

config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['okx']['api_key']
api_secret = config['okx']['api_secret']
password = config['okx']['password']

exchange = ccxt.bingx({
    'apiKey': api_key ,
    'secret': api_secret,
    'options': {
        'adjustForTimeDifference': True,
        'defaultType': 'future',
    },
})
