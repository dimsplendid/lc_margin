import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Union

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
        self.psh = float(df['PSH'][0])
        
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
        
    @property
    def lc_margin(self):
        # print(self.psh)
        return self.predict[0] * self.psh * 100
    

def liquid_crystal_margin_calculator(
    data:pd.DataFrame
) -> Dict[Fab,pd.DataFrame]:
    """
    data: pd.DataFrame
        data should have the following columns:
        - Fab
        - Glass
        - PS Model
        - MPS Type
        - LC Type
        ...
    """    
    # separate T1 and T2 data
    result = {
        Fab.T1: data[data['Fab'] == Fab.T1.label].copy(),
        Fab.T2: data[data['Fab'] == Fab.T2.label].copy(),
    }
    
    # define some one-hot encoding mappings
    
    def map_fab(x:str):
        return 1
    
    def map_glass(x:str):
        return 1
    
    def map_ps(x:str, fab:Fab) -> pd.Series:
        if fab == Fab.T1:
            return pd.Series({
                PSModel.PS_700R_1.label: [1, 0, 0],
                PSModel.PS_NN4104.label: [0, 1, 0],
                PSModel.PS_TG1553SA7.label: [0, 0, 1],
            }[x])
        elif fab == Fab.T2:
            return pd.Series({
                PSModel.PS_214_R5.label: [1, 0],
                PSModel.PS_TG1553SA7.label: [0, 1]
            }[x])
        else:
            raise(f"Fab {fab} not supported")
        
    def map_mps_type(x:str) -> pd.Series:
        return pd.Series({
            MPSType.C.label: [1, 0, 0],
            MPSType.O.label: [0, 1, 0],
            MPSType.T.label: [0, 0, 1],
        }[x])
        
    def map_lc_type(x:str) -> pd.Series:
        return pd.Series({
            LCType.NLC.label: [1, 0],
            LCType.PLC.label: [0, 1],
        }[x])
    
    for fab, df in result.items():
        if len(df) == 0:
            continue
        # loading model
        if fab == Fab.T1:
            with open(MODLE_PATH / 'T1_GBR.pickle.dat', 'rb') as f:
                model = pickle.load(f)   
        else:
            model = XGBRegressor()
            model.load_model(MODLE_PATH / 'T2_XGB.bin')
        
        # re-build input file
        df_mid_list = []
        df_mid_list.append(df['Fab'].apply(map_fab))
        df_mid_list.append(df['Glass'].apply(map_glass))
        df_mid_list.append(df['PS Model'].apply(map_ps, fab=fab))
        df_mid_list.append(df['MPS Type'].apply(map_mps_type))
        df_mid_list.append(df['LC Type'].apply(map_lc_type))
        
        df_mid = pd.concat(df_mid_list, axis=1)
        
        df_front = df.iloc[:, 5:]
    
        df_front.insert(
            6, 
            'MPS Density', 
            np.pi/4 * df_front['MPS Top']**2 * df_front['MPS No.']
            / (df_front['pixel size']**2 * df_front['Repeat unit']) * 100
        )

        # SPS Density

        df_front.insert(
            12,
            'SPS Density',
            np.pi/4 * df_front['SPS TopX']**2 * df_front['SPS No.']
            / (df_front['pixel size']**2 * df_front['Repeat unit']) * 100
        )

        # 1st Density

        df_front.insert(
            15, 
            '1st Density', 
            df_front['MPS CArea 1st'] * df_front['MPS No.']
            / (df_front['pixel size']**2 * df_front['Repeat unit']) * 100
        )

        # 2nd Density

        df_front.insert(
            16, 
            '2nd Density', 
            df_front['MPS CArea 2nd'] * df_front['MPS No.']
            / (df_front['pixel size']**2 * df_front['Repeat unit']) * 100
        )

        # 3rd Density

        df_front.insert(
            17, 
            '3rd Density', 
            np.pi/4 * df_front['MPS Top']**2 * df_front['MPS No.']
            / (df_front['pixel size']**2 * df_front['Repeat unit']) * 100
        )
        # CF Glass area

        df_front['CF Glass area'] = (
            df_front['CF Glass width'] * df_front['CF Glass length'] / 100
        )

        # TFT Glass area

        df_front['TFT Glass area'] =(
            df_front['TFT Glass width'] * df_front['TFT Glass length'] / 100
        )

        # CF Glass diagonal

        df_front['CF Glass diagonal'] = np.linalg.norm(
            [df_front['CF Glass width'], df_front['CF Glass length']],
            axis=0,
        )

        # TFT Glass diagonal

        df_front['TFT Glass diagonal'] = np.linalg.norm(
            [df_front['TFT Glass width'], df_front['TFT Glass length']],
            axis=0,
        )

        # inch_size

        df_front['inch_size'] = np.linalg.norm(
            [df_front['TFT Glass width'], df_front['TFT Glass length']],
            axis=0,
        ) / 2.54 / 10
        
        df_end = pd.DataFrame({
            "MPS_Volume": np.pi/12 * df_front['PSH'] * 
            (
                df_front['MPS Top']**2 
                + df_front['MPS Top']*df_front['MPS Bottom'] 
                + df_front['MPS Bottom']**2
            ),
            "SPS_Volume": np.pi/4 * (
                df_front['SPS TopX'] * df_front['SPS TopY']
                * (df_front['PSH']-0.45)
                + (df_front['PSH']-0.45)/6 
                * (
                    2*df_front['SPS BottomX']
                    *df_front['SPS BottomY']
                    +df_front['SPS TopX']*df_front['SPS BottomY']
                    +df_front['SPS TopY']*df_front['SPS BottomX']
                    -4*df_front['SPS TopX']*df_front['SPS TopY']
                    )
            ),
        })

        df_end['MPS_Volume_per_unit'] = (
            100 * df_end['MPS_Volume'] * df_front['MPS No.'] 
                / (df_front['pixel size']**2 * df_front['Repeat unit'])
        )
        df_end['SPS_Volume_per_unit'] = (
            100 * df_end['SPS_Volume'] * df_front['SPS No.'] 
                / (df_front['pixel size']**2 * df_front['Repeat unit'])
        )

        df_end['Glass_weight'] = (
            df_front['Glass thickness'] 
            * df_front['CF Glass width'] 
            * df_front['CF Glass length'] * 9.8 * 2.44
        )
        
        input_df = pd.concat([df_front, df_mid, df_end], axis=1)
        df['Density'] = input_df['1st Density']
        df['允壓量範圍(um)'] = model.predict(input_df)
        df['LC Margin'] = df['允壓量範圍(um)'] * df['PSH'] * 100
        # input_df.to_excel('input.xlsx')
    return result