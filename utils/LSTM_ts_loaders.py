import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader, TensorDataset


class TS_loaders():
    def __init__(self, train, test=None, 
                 n_input=21, n_output=7):
        self.train = train
        self.test = test
        self.n_input = n_input
        self.n_output = n_output       
        
    def scaling(self, x, action):
        '''normalization'''
        if action == 'fit':
            self.scaler = MinMaxScaler()
            train_norm = self.scaler.fit_transform(x.values.reshape(-1, 1))
            return train_norm
        if action == 'transform':
            test_norm = self.scaler.transform(x.values.reshape(-1, 1))
            return test_norm
    
    def inv_scaler(self, x):
        '''for inverse values'''
        return self.scaler.inverse_transform(x)
      
    def sliding_windows(self, sequences):
        '''creating windows'''
        X, y = [], []
        for i in range(len(sequences)):
            end_ix = i + self.n_input
            out_end_ix = end_ix + self.n_output
            if out_end_ix > len(sequences): 
                break
            seq_x = sequences[i:end_ix]
            seq_y = sequences[end_ix:out_end_ix]
            X.append(seq_x)
            y.append(seq_y)
        
        return np.array(X).astype(np.float32), np.array(y).astype(np.float32)

    def loaders(self, batch_size=1):
        '''combining all steps for dataloaders'''
        train_norm = self.scaling(self.train, action='fit')
        test_norm = self.scaling(self.test, action='transform')
        X_train, y_train = self.sliding_windows(train_norm)
        X_test, y_test = self.sliding_windows(test_norm)
        
        X_train_tens = torch.tensor(X_train)
        y_train_tens = torch.tensor(y_train).squeeze(-1)
        X_test_tens = torch.tensor(X_test)
        y_test_tens = torch.tensor(y_test).squeeze(-1)
        
        train_loader = DataLoader(TensorDataset(X_train_tens , y_train_tens), batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(TensorDataset(X_test_tens , y_test_tens), batch_size=batch_size, shuffle=False)
        
        return train_loader, test_loader