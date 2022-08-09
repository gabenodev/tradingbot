import pandas as pd
import numpy as np

# Signal class designed to give "Buy" signals by creating a new column with 0 or 1 values

class Signal:

    def __init__(self, df):
        self.df = df

    """
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
    """

    def decide_based_on_RSI(self):
        self.df['Buy'] = np.where((self.df['rsi'] < 30) & (self.df['EMA50'] > self.df['EMA200']), 1, 0)