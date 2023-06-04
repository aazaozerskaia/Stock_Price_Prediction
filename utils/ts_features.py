import pandas as pd

class ts_features:
    def __init__(self, data, y='adj close',
                 lag_orders=None, ma_windows=None):
        self.data = data     
        self.y = y
        self.lag_orders = lag_orders
        self.ma_windows = ma_windows
        self.min_lag = min(lag_orders) # for using ma in prediction

    def add_lags(self):
        '''add lags with given orders'''
        if len(self.lag_orders) < 1: return
        df = self.data.copy()
        for l in self.lag_orders:
            df[f'lag_{l}_{self.y}'] = df.groupby(['symbol'])[self.y].shift(l).fillna(0)
        self.data = df
        
    def add_ma(self):
        '''add MA with given window'''
        if len(self.ma_windows) < 1: return  
        df = self.data.copy()
        for day in self.ma_windows:
            df[f'ma_{day}_{self.y}'] = df.groupby('symbol')[self.y].transform(lambda x: x.rolling(day, 1).mean())
        self.data = df
        
    def add_ma_for_pred(self):
        '''add MA for prediction based on lagged values'''
        if len(self.ma_windows) < 1: return
        df = self.data.copy()
        for day in self.ma_windows:
            df[f'ma_{day}_lag_{self.y}'] = df.groupby('symbol')[f'lag_{self.min_lag}_{self.y}']. \
                                  transform(lambda x: x[x!= 0].rolling(day, 1).mean()). \
                                  fillna(0)
        self.data = df   
    
    def add_features(self):
        '''apply functions to data'''
        if self.lag_orders is not None: self.add_lags()
        if self.ma_windows is not None: self.add_ma() 
        if ((self.ma_windows is not None) and (self.lag_orders is not None)): self.add_ma_for_pred() 
        return self.data
        