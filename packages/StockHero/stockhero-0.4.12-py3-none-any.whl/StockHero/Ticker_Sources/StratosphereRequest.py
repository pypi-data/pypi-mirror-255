# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 10:53:30 2023

@author: rwenzel
Version: 0.4.12
"""

# Packages
import pandas as pd
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import numpy as np

# Header
from .TickerRequest import *

class StratosphereRequest(TickerRequest):
    def __init__(self, ticker, headers_standard):
        super().__init__(ticker, headers_standard)
        self.__headers_standard = headers_standard
         
    ###########################
    ###                     ###
    ###    Stratosphere     ###
    ###      Requests       ###
    ###                     ###
    ###########################
    
    @property
    def basic(self):
        return self.__stratosphere_basic_abfrage()
    
    @property
    def margins(self):
        return self.__stratosphere_margins_abfrage()
    
    @property
    def returns(self):
        return self.__stratosphere_returns_abfrage()
    
    @property
    def valuation_ttm(self):
        return self.__stratosphere_valuation_ttm_abfrage()
    
    @property
    def valuation_ntm(self):
        return self.__stratosphere_valuation_ntm_abfrage()
    
    @property
    def per_share(self):
        return self.__stratosphere_per_share_abfrage()
    
    @property
    def growth(self):
        return self.__stratosphere_growth_abfrage()
    
    @property
    def dividends(self):
        return self.__stratosphere_dividends_abfrage()
    
    @property
    def summary(self):
        return self.__stratosphere_summary_abfrage()
    
    ###########################
    ###                     ###
    ###    Stratosphere     ###
    ###        Dummy        ###
    ###                     ###
    ###########################
    
    # Dummy Abfragen, um Fehler im Vorfeld abzufangen
    def __stratosphere_basic_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_basic_df()
    
    def __stratosphere_margins_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_margins_df()
    
    def __stratosphere_returns_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_returns_df()
    
    def __stratosphere_valuation_ttm_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_valuation_ttm_df()
    
    def __stratosphere_valuation_ntm_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_valuation_ntm_df()
    
    def __stratosphere_per_share_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_per_share_df()
    
    def __stratosphere_growth_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_growth_df()
    
    def __stratosphere_dividends_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_dividends_df()
    
    def __stratosphere_summary_abfrage(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__stratosphere_summary_df()
    
    ###########################
    ###                     ###
    ###     Stratosphere    ###
    ###    Help functions   ###
    ###                     ###
    ###########################
    
    # Hilfsfunktionen 
    def __initialize_dataframe(self, index):
        df = pd.DataFrame([''], columns=["Summary"], index=index)
        return df

    ###########################
    ###                     ###
    ###     Stratosphere    ###
    ###        Search       ###
    ###                     ###
    ###########################

    # Suche bei https://www.stratosphere.io/
    def __stratosphere_identifier(self):
        
        params = {
            "x-algolia-agent": "Algolia for JavaScript (5.0.0-alpha.73); Search (5.0.0-alpha.73); Browser",
            "x-algolia-api-key": "f490c20728b7866fc81c7b6e3d7e0e2b",
            "x-algolia-application-id": "ZPBCEGHCCC",
        }
        
        url = "https://zpbceghccc-dsn.algolia.net/1/indexes/*/queries?" + urlencode(params)

        try:
            data = {"requests":[{"indexName":"companies","query":f"{self.ticker}","hitsPerPage":1,"tagFilters":["Stratosphere"]}]}
            page = requests.post(url, json=data)
            json = page.json()
            self.__identifier = json["results"][0]["hits"][0]["identifier"]
            self.name = json["results"][0]["hits"][0]["name"]
        except:
            return None
        
        return self.__identifier

    ###########################
    ###                     ###
    ###     Stratosphere    ###
    ###         Data        ###
    ###                     ###
    ###########################
    
    # Eigentlichen Abfragen
    def __stratosphere_data_dict(self):
        
        url = f'https://www.stratosphere.io/company/{self.__stratosphere_identifier()}/'
        #url = f'https://www.finchat.io/company/{self.__stratosphere_identifier()}/'

        page = requests.get(url, headers=self.__headers_standard)
        
        if page.status_code != 200:
            return None
          
        page = BeautifulSoup(page.content, 'html.parser')

        """
        Der Header der Tabelle, quasi der Column Label
        Ausgabe als Liste
        """

        content = page.find('div', {'class':'w-full columns-1 gap-x-2.5 @sm:columns-2 @md:columns-3'}).find_all(string = True)
        
        data = [
            (content[0], content[1], content[2]),
            (content[0], content[3], content[4]),
            (content[0], content[5], content[6]),
            (content[0], content[7], content[8]),
            (content[0], content[9], content[10]),
            
            (content[11], content[12], content[13]),
            (content[11], content[14], content[15]),
            (content[11], content[16], content[17]),
            (content[11], content[18], content[19]),
            (content[11], content[20], content[21]),
            (content[11], content[22], content[23]),
            
            (content[24], content[25], content[26]),
            (content[24], content[27], content[28]),
            (content[24], content[29], content[30]),
            (content[24], content[31], content[32]),
            
            (content[33], content[34], content[35]),
            (content[33], content[36], content[37]),
            (content[33], content[38], content[39]),
            (content[33], content[40], content[41]),
            (content[33], content[42], content[43]),
            (content[33], content[44], content[45]),
            
            (content[46], content[47], content[48]),
            (content[46], content[49], content[50]),
            (content[46], content[51], content[52]),
            (content[46], content[53], content[54]),
            (content[46], content[55], content[56]),
            
            (content[57], content[58], content[59]),
            (content[57], content[60], content[61]),
            (content[57], content[62], content[63]),
            (content[57], content[64], content[65]),
            
            (content[66], content[67], content[68]),
            (content[66], content[69], content[70]),
            (content[66], content[71], content[72]),
            (content[66], content[73], content[74]),
            (content[66], content[75], content[76]),
            (content[66], content[77], content[78]),
            (content[66], content[79], content[80]),
            (content[66], content[81], content[82]),
            (content[66], content[83], content[84]),
            (content[66], content[85], content[86]),
            
            (content[87], content[88], content[89]),
            (content[87], content[90], content[91]),
            (content[87], content[92], content[93]),
            (content[87], content[94], content[95]),
            (content[87], content[96], content[97]),
            (content[87], content[98], content[99]),
            (content[87], content[100], content[101]),
        ]
        
        dfs = {}
        
        for col, idx, val in data:
            if col not in dfs:
                dfs[col] = pd.DataFrame(columns=[col])
            dfs[col].loc[idx] = val
        
        dict_stratosphere_summary = dfs 
    
        return dict_stratosphere_summary

    # Basic
    def __stratosphere_basic_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_basic = data["Basic"]
        else:
            return data
        
        return df_stratosphere_basic
    
    # Margins
    def __stratosphere_margins_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_margins = data["Margins"]
        else:
            return data
        
        return df_stratosphere_margins
    
    # Returns (5Yr Avg)
    def __stratosphere_returns_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_returns = data["Returns (5Yr Avg)"]
        else:
            return data
        
        return df_stratosphere_returns
    
    # Valuation (TTM)
    def __stratosphere_valuation_ttm_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_valuation_ttm = data["Valuation (TTM)"]
        else:
            return data
        
        return df_stratosphere_valuation_ttm
    
    # Valuation (NTM)
    def __stratosphere_valuation_ntm_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_valuation_ntm = data["Valuation (NTM)"]
        else:
            return data
        
        return df_stratosphere_valuation_ntm
    
    # Per Share
    def __stratosphere_per_share_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_per_share = data["Per Share"]
        else:
            return data
        
        return df_stratosphere_per_share
    
    # Growth (CAGR)
    def __stratosphere_growth_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_growth = data["Growth (CAGR)"]
        else:
            return data
        
        return df_stratosphere_growth
    
    # Dividends
    def __stratosphere_dividends_df(self):
        
        data = self.__stratosphere_data_dict()
        
        if data != None:
            df_stratosphere_dividends = data["Dividends"]
        else:
            return data
        
        return df_stratosphere_dividends
    
    # All
    def __stratosphere_summary_df(self):
        
        data = self.__stratosphere_data_dict()
        
        df1_1 = self.__initialize_dataframe(data["Basic"].columns)
        df2_1 = self.__initialize_dataframe(data["Margins"].columns)
        df3_1 = self.__initialize_dataframe(data["Returns (5Yr Avg)"].columns)
        df4_1 = self.__initialize_dataframe(data["Valuation (TTM)"].columns)
        df5_1 = self.__initialize_dataframe(data["Valuation (NTM)"].columns)
        df6_1 = self.__initialize_dataframe(data["Per Share"].columns)
        df7_1 = self.__initialize_dataframe(data["Growth (CAGR)"].columns)
        df8_1 = self.__initialize_dataframe(data["Dividends"].columns)

        df_stratosphere_summary = pd.concat([df1_1, data["Basic"].rename(columns={'Basic': 'Summary'}),
                                             df2_1, data["Margins"].rename(columns={'Margins': 'Summary'}),
                                             df3_1, data["Returns (5Yr Avg)"].rename(columns={'Returns (5Yr Avg)': 'Summary'}),
                                             df4_1, data["Valuation (TTM)"].rename(columns={'Valuation (TTM)': 'Summary'}),
                                             df5_1, data["Valuation (NTM)"].rename(columns={'Valuation (NTM)': 'Summary'}),
                                             df6_1, data["Per Share"].rename(columns={'Per Share': 'Summary'}),
                                             df7_1, data["Growth (CAGR)"].rename(columns={'Growth (CAGR)': 'Summary'}),
                                             df8_1, data["Dividends"].rename(columns={'Dividends': 'Summary'})
                                             ], axis=0)
        
        return df_stratosphere_summary