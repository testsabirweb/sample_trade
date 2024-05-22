import pandas as pd

class Config:
    def __init__(self):
        # Variables
        self.c_flag = 0
        self.p_flag = 0
        self.p_pos = 0
        self.c_pos = 0
        self.c_strike = ""
        self.p_strike = ""
        self.row = -1
        self.c_stoploss = 0
        self.c_entry = 0
        self.c_target = 0
        self.c_gain = 0
        self.p_stoploss = 0
        self.p_entry = 0
        self.p_target = 0
        self.p_gain = 0
        self.expiry = ""
        self.sym = "NSE:NIFTYBANK-INDEX"
        self.fmflag = 0
        self.fimflag = 0
        self.data_5_timeframe = pd.DataFrame()
        self.data_15_timeframe = pd.DataFrame()
        self.current_data_5_timeframe = pd.DataFrame()
        self.current_data_15_timeframe = pd.DataFrame()