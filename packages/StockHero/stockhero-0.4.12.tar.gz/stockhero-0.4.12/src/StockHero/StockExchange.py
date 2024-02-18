# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 18:02:49 2022

@author: RobWen
Version: 0.4.9
"""
import pandas as pd
import requests
from pandas import json_normalize
from bs4 import BeautifulSoup

    #########################
    ###                   ###
    ###  Stock exchanges  ###
    ###     indicies      ###
    ###                   ###
    #########################
        
class StockExchange:

    def __init__(self, stockexchange):
        self.stockexchange = stockexchange
        self.__headers_standard = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}
        
    def __repr__(self):
        return(self.stockexchange)
        
    def __str__(self):
        return(self.stockexchange)
    
    #####################
    ###               ###
    ###    NASDAQ     ###
    ###               ###
    #####################
    
    @property
    def nasdaq(self):
        return self.__df_nasdaq()
    
    #####################
    ###               ###
    ###      CNN      ###
    ###               ###
    #####################
    
    @property
    def cnn_fear_and_greed(self):
        return self.__cnn_fear_and_greed_df()
    
    @property
    def cnn_fear_and_greed_graph_data(self):
        return self.__cnn_fear_and_greed_graph_data_df()
    
    ##########################
    ###                    ###
    ###      Börsen        ###
    ###  Hamburg-Hannover  ###
    ###                    ###
    ##########################
    
    ''' Down since 23.06.2022
    
    @property
    def dax(self):
        return self.__boersenag_dax_df()
    
    @property
    def mdax(self):
        return self.__boersenag_mdax_df()
    
    @property
    def sdax(self):
        return self.__boersenag_sdax_df()
    
    @property
    def tecdax(self):
        return self.__boersenag_tecdax_df()
    
    @property
    def nisax(self):
        return self.__boersenag_nisax_df()
    
    @property
    def haspax(self):
        return self.__boersenag_haspax_df()
    
    @property
    def eurostoxx(self):
        return self.__boersenag_eurostoxx_df()
    
    @property
    def gcx(self):
        return self.__boersenag_gcx_df()
    
    @property
    def gevx(self):
        return self.__boersenag_gevx_df()
    
    @property
    def gergenx(self):
        return self.__boersenag_gergenx_df()
    
    @property
    def dow_jones(self):
        return self.__boersenag_dow_jones_df()
    
    @property
    def nasdaq_100(self):
        return self.__boersenag_nasdaq_100_df()
    
    '''
    
    #####################
    ###               ###
    ###    NASDAQ     ###
    ###               ###
    #####################
    
    ### NASDQ Stock Screener                                   ###
    ### https://www.nasdaq.com/market-activity/stocks/screener ###
    def __df_nasdaq(self):
        r = requests.get("https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true", headers=self.__headers_standard)
        
        json = r.json()
               
        json_data = json['data']['rows']
        df = json_normalize(json_data)
        json_headers = json['data']['headers']
        df_headers = json_normalize(json_headers)
        df_nasdaq_stockexchange = df.rename(columns=df_headers.loc[0])
        
        return df_nasdaq_stockexchange
    
    #####################
    ###               ###
    ###      CNN      ###
    ###               ###
    #####################
    
    ### CNN Fear and Greed Index                   ###
    ### https://money.cnn.com/data/fear-and-greed/ ###
    
    def __cnn_fear_and_greed_df(self):
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=self.__headers_standard)
        json = r.json()
        
        try:
            def fear_greed_f(fear_greed):
              wert = int(round(fear_greed))
              
              if wert < 0:
                  fear_greed_rating = 'Cant read values'
              elif wert < 25:
                  fear_greed_rating = 'Extreme Fear'
              elif wert < 46:
                  fear_greed_rating = 'Fear'
              elif wert < 55:
                  fear_greed_rating = 'Neutral'
              elif wert < 76:
                    fear_greed_rating = 'Greed'
              elif wert <= 100:
                    fear_greed_rating = 'Extreme Greed'
              else:
                    fear_greed_rating = 'Cant read values'
                    
              return fear_greed_rating
            
            df_cnn_fear_and_greed = pd.DataFrame(
                                [
                                [json['fear_and_greed']['score'], fear_greed_f(json['fear_and_greed']['score'])],
                                [json['fear_and_greed']['previous_close'], fear_greed_f(json['fear_and_greed']['previous_close'])],
                                [json['fear_and_greed']['previous_1_week'], fear_greed_f(json['fear_and_greed']['previous_1_week'])],
                                [json['fear_and_greed']['previous_1_month'], fear_greed_f(json['fear_and_greed']['previous_1_month'])],
                                [json['fear_and_greed']['previous_1_year'], fear_greed_f(json['fear_and_greed']['previous_1_year'])],
                                ]
                                
                                , index = ['Current', 'Previous close', '1 week ago', '1 month ago', '1 year ago']
                                , columns = ['Score', 'Rating'])
                       
            return df_cnn_fear_and_greed
        except:
            return None
        
    ### CNN Fear and Greed Index                   ###
    ### https://money.cnn.com/data/fear-and-greed/ ###
    
    def __cnn_fear_and_greed_graph_data_df(self):
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=self.__headers_standard)
        json = r.json()
        
        try:
            df_cnn_fear_and_greed_graph_data = json
            return df_cnn_fear_and_greed_graph_data
        except:
            return None
        
    ##########################
    ###                    ###
    ###      Börsen        ###
    ###  Hamburg-Hannover  ###
    ###                    ###
    ##########################
    
    ### DAX Performance-Index                           ###
    ### 40 Werte                                        ###

    def __boersenag_dax_df(self):
        
            return None
        
    ### MDAX Performance-Index                            ###
    ### 50 Werte                                          ###
    
    def __boersenag_mdax_df(self):

            return None
        
    ### SDAX Performance-Index                            ###
    ### 70 Werte                                          ###
    
    def __boersenag_sdax_df(self):

            return None
    
    ### TecDAX Performance-Index                            ###
    ### 30 Werte                                            ###
    
    def __boersenag_tecdax_df(self):

            return None
    
    ### NISAX 20 Index (Net Return) (EUR)                   ###
    ### 20 Werte                                            ###
    
    def __boersenag_nisax_df(self):

            return None
    
    ### Haspax Index (Performance) (EUR)                   ###
    ### 22 Werte (01.12.2021)                              ###
    
    def __boersenag_haspax_df(self):

            return None
        
    ### EURO STOXX 50 Index (Price) (EUR)                       ###
    ### 50 Werte                                                ###
    
    def __boersenag_eurostoxx_df(self):

            return None
    
    ### GCX Global Challenges Performance-Index         ###
    ### 50 Werte                                        ###
    
    def __boersenag_gcx_df(self):

            return None

    ### Global Ethical Values Index (Total Return) (EUR)  ###
    ### 609 Werte (variable)                              ###
    
    def __boersenag_gevx_df(self):

            return None

    ### German Gender Index (Total Return) (EUR)                       ###
    ### 50 Werte                                                       ###
    
    def __boersenag_gergenx_df(self):

            return None


    ### Dow Jones Industrial Average Index (Price) (USD)       ###
    ### 30 Werte (fix) - Fehler hier nur 29 Werte (01.12.2021) ###
    
    def __boersenag_dow_jones_df(self):

            return None

    ### Nasdaq-100 Index                                        ###
    ### 100 Werte (fix) - Fehler hier nur 86 Werte (01.12.2021) ###
    
    def __boersenag_nasdaq_100_df(self):

            return None

###############################################################################
###############################################################################
    