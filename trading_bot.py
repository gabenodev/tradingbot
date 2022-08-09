API_KEY = "OnYtZaENGz5szLK5QAwTsz2EDrsc8Rdu9DQzLqzup1xEilqzzWyFuLku8eOhASrT"
SECRET_KEY = "GmZmw5BcKNCk370iKtbdhqfsENpFt9QJpNLAoxBV4Lexxc9VWC49460jfnZkmxq4"

from binance.client import Client
import pandas as pd
import ta
import numpy as np
import time

client = Client(API_KEY, SECRET_KEY)
info = client.get_symbol_info('BNBBTC')


def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                      interval,
                                                      lookback + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def applytechnicals(df):
    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['macd'] = ta.trend.macd_diff(df.Close)
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['EMA50'] = ta.trend.ema_indicator(df.Close, window=50)
    df['EMA200'] = ta.trend.ema_indicator(df.Close, window=200)
    # Stochastic RSI
    #df['Srsi'] = ta.momentum.StochRSIIndicator(df.Close, window=14, smooth1=3, smooth2=3)
    df.dropna(inplace=True)


df = getminutedata('ADAUSDT', '5m', '2000')
applytechnicals(df)
#print(df)


class Signals:

    def __init__(self, df, lags):
        self.df = df
        self.lags = lags

    def gettrigger(self):
        dfx = pd.DataFrame()
        masks = []
        for i in range(self.lags + 1):
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
            masks.append(mask)
        dfx = pd.concat(masks, ignore_index=True)
        return dfx.sum(axis=0)

    def decide(self):
        self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
        self.df['Buy'] = np.where(self.df.trigger
                                  & (self.df['%D'].between(20, 80))
                                  & (self.df.rsi > 50)
                                  & (self.df.macd > 0), 1, 0)

    def decide_based_on_RSI(self):
        self.df['Buy'] = np.where((self.df['rsi'] < 30) & (self.df['EMA50'] > self.df['EMA200']), 1, 0)


inst = Signals(df, 25)
inst.decide_based_on_RSI()
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)
print(df[df.Buy == 1])


def strategy(pair, qty, open_position=False):
    df = getminutedata(pair, '5m', '2000')
    applytechnicals(df)
    inst = Signals(df, 25)
    inst.decide()
    print(f'current candle Close is ' + str(df.Close.iloc[-1]))
    clear = "\n" * 3
    print(clear)
    if df.Buy.iloc[-1]:
        order = client.create_order(symbol=pair,
                                    side='BUY',
                                    type='MARKET',
                                    quantity=qty)
        print(order)
        buyprice = float(order['fills'][0]['price'])

        open_position = True
        while open_position:
            time.sleep(0.5)
            df = getminutedata(pair, '1m', '2')
            print(f'OP - current candle Close ' + str(df.Close.iloc[-1]))
            print(f'Buying price is ' + str(buyprice))
            print('-----------------------------------------')
            print(f'Until closing position ' + str(buyprice * 1.00231))
            print(f'current Stop Loss is ' + str(buyprice * 0.9985))

            clear = "\n" * 2
            print(clear)
            if df.Close[-1] <= buyprice * 0.9985:
                order = client.create_order(symbol=pair,
                                            side='SELL',
                                            type='MARKET',
                                            quantity=qty)
                print(order)
                break

            if df.Close[-1] >= 1.00231 * buyprice:
                order = client.create_order(symbol=pair,
                                            side='SELL',
                                            type='MARKET',
                                            quantity=qty)
                print(order)
                break


def strategy_RSI_EMA(pair, qty, open_position=False):
    df = getminutedata(pair, '5m', '2000')
    applytechnicals(df)
    inst = Signals(df, 25)
    inst.decide_based_on_RSI()
    print(f'current candle Close is ' + str(df.Close.iloc[-1]))
    print(f'current RSI is ' + str(df.rsi[-1]))
    clear = "\n" * 3
    print(clear)
    if df.Buy.iloc[-1]:
        order = client.create_order(symbol=pair,
                                    side='BUY',
                                    type='MARKET',
                                    quantity=qty)
        print(order)
        buyprice = float(order['fills'][0]['price'])

        open_position = True
        while open_position:
            time.sleep(0.5)
            df = getminutedata(pair, '1m', '2')
            print(f'OP - current candle Close ' + str(df.Close.iloc[-1]))
            print(f'Buying price is ' + str(buyprice))
            print('-----------------------------------------')
            print(f'current RSI is ' + str(df.rsi[-1]))
            print(f'current Stop Loss is ' + str(buyprice * 0.99))

            clear = "\n" * 2
            print(clear)

            if df.Close[-1] <= buyprice * 0.99:
                order = client.create_order(symbol=pair,
                                            side='SELL',
                                            type='MARKET',
                                            quantity=qty)
                print(order)
                break

            if df.rsi[-1] >= 67:
                order = client.create_order(symbol=pair,
                                            side='SELL',
                                            type='MARKET',
                                            quantity=qty)
                print(order)
                break


while True:
    strategy_RSI_EMA('BTCBUSD', 0.0018)
    time.sleep(1)
