import Signal
import API
import Data
import Strategy
from binance.client import Client
import pandas as pd
import ta
import numpy as np
import time

client = Client(API.API_KEY, API.SECRET_KEY)
info = client.get_symbol_info('BNBBTC')

def displayOptions():
    pd.options.display.width = None
    pd.options.display.max_columns = None
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 3000)

displayOptions()
df = Data.getMinuteData('BTCBUSD', '5m', '2000')
Strategy.applytechnicals(df)
#print(df)

inst = Signal.Signal(df)
inst.decide_based_on_RSI()

print(df[df.Buy == 0])


while True:
    Strategy.strategy_RSI_EMA('BTCBUSD', 0.0018)
    time.sleep(1)
