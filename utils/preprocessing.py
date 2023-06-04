import pandas as pd
import numpy as np
import itertools


class data_preprocessing:
    def __init__(self, data, 
                 add_all_dates=False):
        
        data.columns = data.columns.str.lower()
        self.data = data
        self.start_date = data['date'].min()
        self.end_date = data['date'].max()
        self.symbols = sorted(data['symbol'].unique())
        self.add_all_dates = add_all_dates
            
    def add_all_dates_(self):
        '''Add missing days for all tickers'''
        date_list = pd.date_range(start=self.start_date, end=self.end_date).tolist()
        keys = list(itertools.product(date_list, self.symbols))
        keys_df = pd.DataFrame(keys, columns=['date', 'symbol'])
        df = self.data.copy()
        df = pd.merge(keys_df, df, how="left", on=['date', 'symbol'])
        self.data = df

    def fill_nan(self):
        '''Fill missing values with previous ones'''  
        # delete first missing values
        df = self.data.copy()
        df = df[df['date'] >= self.start_date]
        # delete non actual tickers
        df = df[df['symbol'].isin(self.actual_tickers())].reset_index(drop=True)

        if self.add_all_dates:
            df['is_working'] = np.where(df['adj close'].isna(), 0, 1)
        
        for s in self.symbols:
            df[df['symbol']==s] = df[df['symbol']==s].fillna(method='ffill')
        # other fill with 0
        df = df.fillna(0)
        df = df[df['gics sector'] != 0].reset_index(drop=True) 
        self.data = df

    def actual_tickers(self):
        '''Leave only currently available tickers'''
        df_wo_na = self.data.dropna(subset=['adj close'])
        check_df = df_wo_na.groupby('symbol').agg(max_date=('date', 'max')).reset_index()
        act_symb_list = check_df[check_df['max_date'] == self.end_date]['symbol'].tolist()
        return act_symb_list

    def preprocessing_steps(self):
        '''combining all steps'''
        if self.add_all_dates:
            self.add_all_dates_()
        self.fill_nan()
        return self.data
            