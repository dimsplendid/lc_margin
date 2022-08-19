import pickle
from pathlib import Path

from xgboost import XGBRegressor
import numpy as np
import pandas as pd

from ..models import (
    Fab,
    Glass,
    PSModel,
    MPSType,
    LCType,
)

MODLE_PATH = Path(__file__).resolve(strict=True).parent / 'models'

class LCMarginCalculator:
    def __init__(
        self, 
        fab: str,
        glass: str,
        ps_model: str,
        mps_type: str,
        lc_type: str,
        others: pd.DataFrame,
    ):
        if fab == Fab.T1.label:
            with open(MODLE_PATH / 'T1_GBR.pickle.dat', 'rb') as f:
                self.model = pickle.load(f)
            self.fab = [1]
            self.ps_model = {
                PSModel.PS_700R_1.label: [1, 0, 0],
                PSModel.PS_NN4104.label: [0, 1, 0],
                PSModel.PS_TG1553SA7.label: [0, 0, 1],
            }[ps_model]
            
        elif fab == Fab.T2.label:
            self.model = XGBRegressor()
            self.model.load_model(MODLE_PATH / 'T2_XGB.bin')
            self.fab = [1]
            self.ps_model = {
                PSModel.PS_214_R5.label: [1, 0],
                PSModel.PS_TG1553SA7.label: [0, 1]
            }[ps_model]
        else:
            raise(f"Fab {fab} model doesn't exist!")
        
        if glass == Glass.EXG.label:
            self.glass = [1]
        else:
            raise(f"Glass {glass} doesn't set up!")
        
        self.mps_type = {
            MPSType.C.label: [1, 0, 0],
            MPSType.O.label: [0, 1, 0],
            MPSType.T.label: [0, 0, 1],
        }[mps_type]
        
        self.lc_type = {
            LCType.NLC.label: [1, 0],
            LCType.PLC.label: [0, 1],
        }[lc_type]
        
        df = others.copy()
        df.insert(
            6, 
            'MPS Density', 
            np.pi/4 * df['MPS Top']**2 * df['MPS No.']
            / (df['pixel size']**2 * df['Repeat unit']) * 100
        )

        # SPS Density

        df.insert(
            12,
            'SPS Density',
            np.pi/4 * df['SPS TopX']**2 * df['SPS No.']
            / (df['pixel size']**2 * df['Repeat unit']) * 100
        )

        # 1st Density

        df.insert(
            15, 
            '1st Density', 
            df['MPS CArea 1st'] * df['MPS No.']
            / (df['pixel size']**2 * df['Repeat unit']) * 100
        )

        # 2nd Density

        df.insert(
            16, 
            '2nd Density', 
            df['MPS CArea 2nd'] * df['MPS No.']
            / (df['pixel size']**2 * df['Repeat unit']) * 100
        )

        # 3rd Density

        df.insert(
            17, 
            '3rd Density', 
            np.pi/4 * df['MPS Top']**2 * df['MPS No.']
            / (df['pixel size']**2 * df['Repeat unit']) * 100
        )
        # CF Glass area

        df['CF Glass area'] = df['CF Glass width'] * df['CF Glass length'] / 100

        # TFT Glass area

        df['TFT Glass area'] = df['TFT Glass width'] * df['TFT Glass length'] / 100

        # CF Glass diagonal

        df['CF Glass diagonal'] = np.linalg.norm(
            [df['CF Glass width'], df['CF Glass length']],
            axis=0,
        )

        # TFT Glass diagonal

        df['TFT Glass diagonal'] = np.linalg.norm(
            [df['TFT Glass width'], df['TFT Glass length']],
            axis=0,
        )

        # inch_size

        df['inch_size'] = np.linalg.norm(
            [df['TFT Glass width'], df['TFT Glass length']],
            axis=0,
        ) / 2.54 / 10
        
        self.front = df[:1].astype('float').to_numpy()
        self.mid = np.array(
            [
                self.fab 
                + self.glass 
                + self.ps_model 
                + self.mps_type 
                + self.lc_type
            ]
        )
        end_df = pd.DataFrame({
            "MPS_Volume": np.pi/12 * others['PSH'] * 
            (others['MPS Top']**2 + others['MPS Top']*others['MPS Bottom'] + others['MPS Bottom']**2),
            "SPS_Volume": np.pi/4 * (
                others['SPS TopX'] * others['SPS TopY']
                * (others['PSH']-0.45)
                + (others['PSH']-0.45)/6 
                * (
                    2*others['SPS BottomX']
                    *others['SPS BottomY']
                    +others['SPS TopX']*others['SPS BottomY']
                    +others['SPS TopY']*others['SPS BottomX']
                    -4*others['SPS TopX']*others['SPS TopY']
                    )
            ),
        })

        end_df['MPS_Volume_per_unit'] = (
            100 * end_df['MPS_Volume'] * others['MPS No.'] 
                / (others['pixel size']**2 * others['Repeat unit'])
        )
        end_df['SPS_Volume_per_unit'] = (
            100 * end_df['SPS_Volume'] * others['SPS No.'] 
                / (others['pixel size']**2 * others['Repeat unit']))

        end_df['Glass_weight'] = (
            others['Glass thickness'] 
            * others['CF Glass width'] * others['CF Glass length'] * 9.8 * 2.44,
        )
        self.end = end_df.astype('float').to_numpy()
                
        self.__data = None
        
    @property
    def predict(self):
        # for testing
        # return np.array([42.0])
        return self.model.predict(self.data)
    
    @property
    def data(self):
        if self.__data is not None:
            return self.__data
        try:
            self.__data = np.concatenate(
                (self.front, self.mid, self.end),
                axis=1,
            )
            return self.__data
        except:
            return None
    
    @data.setter
    def data(self, value):
        self.__data = value