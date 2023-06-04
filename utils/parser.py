import pandas as pd
from tqdm import tqdm
import bs4 as bs
import requests
import yfinance as yf


class data_collection:
    def __init__(self, url=None, 
                 start_date='2010-01-01', 
                 end_date='2023-03-31'):
        self.url = url
        self.start_date = start_date
        self.end_date = end_date
        
    def parse_tickers(self):
        '''Collect dictionary of tickers' info based in SP_500'''
        html = requests.get(self.url)
        soup = bs.BeautifulSoup(html.content, 'html.parser')
        table = soup.find('table', {'class': 'wikitable sortable'})
        df = pd.read_html(str(table))[0]
        df.columns = df.columns.str.lower()
        df['symbol'] = df['symbol'].replace("\.", "-", regex=True)
        symb_data = df.sort_values(by='symbol') 
        self.tickers = symb_data['symbol'].unique().tolist()
        return symb_data
    
    def collect_yf_data(self, tickers):
        '''Collect data using Yfinance API'''
        df_list = []
        df = yf.download(tickers[-1], start=self.start_date, end=self.end_date)
        df['symbol'] = [tickers[-1]] * len(df)
        for i in tqdm(range(len(tickers)-1)):    
            a = yf.download(tickers[i], start=self.start_date, end=self.end_date, progress=False)
            a['symbol'] = [tickers[i]] * len(a)
            df = pd.concat([df, a])  
        yf_data = df.reset_index()
        return yf_data
    
    def get_all_data(self):
        '''Merging all data'''
        symb_data = self.parse_tickers()
        yf_data = self.collect_yf_data(self.tickers)
        cols = ['symbol', 'gics sector', 'gics sub-industry']
        data_merged = pd.merge(yf_data, symb_data[cols], how="left", on=['symbol'])
        data_merged.columns = data_merged.columns.str.lower()
        return data_merged
