import pickle
from pathlib import Path

from xgboost import XGBRegressor
import numpy as np
import pandas as pd

MODLE_PATH = Path(__file__).resolve(strict=True).parent / 'models'

class LCMarginCalculator:
    def __init__(
        self, 
        fab: str,
        # glass: str,
        # ps_model: str,
        # mps_type: str,
        # lc_type: str,
        # others: pd.DataFrame,
    ):
        self.fab = fab
        if self.fab == 'T1':
            with open(MODLE_PATH / 'T1_GBR.pickle.dat', 'rb') as f:
                self.model = pickle.load(f)
        elif self.fab == 'T2':
            self.model = XGBRegressor()
            self.model.load_model(MODLE_PATH / 'T2_XGB.bin')
        else:
            raise(f"Fab {self.fab} model doesn't exist!")
        
        self.__data: np.ndarray = None
    
    @property
    def predict(self):
        # for testing
        return np.array([42.0])
        # return self.model.predict(self.data)
    
    @property
    def data(self):
        if self.__data is not None:
            return self.__data
        try:
            ...
        except:
            return None
    
    @data.setter
    def data(self, value):
        self.__data = value