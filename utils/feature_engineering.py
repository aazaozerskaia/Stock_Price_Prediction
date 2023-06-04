import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder


class feature_engineering:
    def __init__(self, data, y='adj close', 
                 cat_features=None):
        self.data = data     
        self.y = y
        self.cat_features = cat_features
        self.encoders_dict = {}
    
    def create_date_features(self):
        '''Add date features to DataFrame'''
        self.data['year'] = self.data['date'].dt.year
        self.data['month'] = self.data['date'].dt.month
        self.data['day'] = self.data['date'].dt.day_of_year
        #self.data['day_of_week'] = self.data['date'].dt.dayofweek
    
    def scaling(self):
        '''scaling feature to 0-1 range'''
        scaler = MinMaxScaler()
        new_col = self.y + '_norm'
        self.data[new_col] = scaler.fit_transform(self.data[self.y].values.reshape(-1, 1))
        min_val = scaler.data_min_
        max_val = scaler.data_max_
        self.encoders_dict['scaler'] = scaler
    
    def labeling(self):
        '''Transformation of categorical features'''
        if self.cat_features is None:
            return 
        for col in self.cat_features:
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])
            self.encoders_dict[col] = le
    
    def get_enc_dict(self):
        '''save for decoding'''
        return self.encoders_dict
        
    def get_data(self):
        '''apply functions to data'''
        self.create_date_features()
        self.scaling()
        self.labeling()
        return self.data
     