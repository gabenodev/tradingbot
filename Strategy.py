from binance.client import Client
import Data
import ta
import Signal
import API
import time
client = Client(API.API_KEY, API.SECRET_KEY)

# Always use this function before applying a strategy
# Creates desired columns with technical values
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

def strategy(pair, qty, open_position=False):
    df = Data.getMinuteData(pair, '5m', '2000')
    applytechnicals(df)
    inst = Signal.Signal(df)
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
            df = Data.getMinuteData(pair, '1m', '2')
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
    df = Data.getMinuteData(pair, '5m', '2000')
    applytechnicals(df)
    inst = Signal.Signal(df)
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
            df = Data.getMinuteData(pair, '1m', '2')
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