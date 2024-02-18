# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 12:58:05 2022

@author: RobWen
Version: 0.4.1
"""

# Packages
import requests
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
from pandas import json_normalize

# Header
from .TickerRequest import *

class TraderFoxRequest(TickerRequest):
    def __init__(self, ticker, headers_standard):
        super().__init__(ticker, headers_standard)
        self.__headers_standard = headers_standard

    ###################
    ###             ###
    ###  Traderfox  ###
    ###  Requests   ###
    ###             ###
    ###################
    
    ## Traderfox Scoring Systems
    # Qualitäts-Check
    @property
    def wachstum_und_stabilität(self):
        return self.__qualität_wachstum_5y_df()
    
    @property
    def profitabilität_rentabilität(self):
        return self.__qualität_profitabilität_df()
    
    @property
    def kursentwicklung_und_volatilität(self):
        return self.__qualität_kursentwicklung_df()
    
    @property
    def sicherheit_und_bilanz(self):
        return self.__qualität_sicherheit_df()
    
    # Dividenden-Check
    @property
    def dividenden_rendite(self):
        return self.__dividend_rendite_df()
    
    @property
    def dividenden_kontinuität(self):
        return self.__dividend_kontinuität_df()
    
    @property
    def dividenden_wachstum(self):
        return self.__dividend_wachstum_df()
    
    @property
    def dividenden_qualität(self):
        return self.__dividend_qualität_df()
    
    # Wachstums-Check
    @property
    def wachstum(self):
        return self.__wachstum_wachstum_df()
    
    @property
    def trend(self):
        return self.__wachstum_trend_df()
    
    @property
    def finanzierbarkeit_wachstum(self):
        return self.__wachstum_finanzierbarkeit_df()
    
    # Robustheits-Check
    @property
    def performance(self):
        return self.__robustheits_performance_df()
    
    @property
    def volatilität(self):
        return self.__robustheits_volatilität_df()
    
    @property
    def drawdown(self):
        return self.__robustheits_drawdown_df()
    
    @property
    def robustheit_in_abwärtsphasen(self):
        return self.__robustheits_robustheit_df()
    
    # Weitere Scoring Systeme
    # Piotroski F-score
    @property
    def piotroski(self):
        return self.__scoring_piotroski_df()
    
    # AAQS Score
    @property
    def aaqs(self):
        return self.__scoring_aaqs_df()
    
    # Dividendenadel
    @property
    def dividendenadel(self):
        return self.__scoring_dividendenadel_df()
    
    # High-Growth-Investing-Score
    @property
    def high_growth_investing(self):
        return self.__scoring_high_growth_investing_df()
    
    ###################
    ###             ###
    ###  Traderfox  ###
    ###     Data    ###
    ###             ###
    ###################

    # Get Qualitäts-Check
    # https://aktie.traderfox.com/ajax/getStockTDFScore.php
    # Funktioniert
    def __qualität_wachstum_5y_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"quality",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][0]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][0]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][0]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][0]['children'][3]['value']
                
                json_column_1 = json['data']['score']['children'][0]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][0]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][0]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][0]['children'][3]['name']
                
                array_data = np.array([json_data_1, json_data_2, json_data_3, json_data_4])
                array_index = np.array([json_column_1, json_column_2, json_column_3, json_column_4])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Wachstum und Stabilität ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__wachstum_5y_df = df
    
        return self.__wachstum_5y_df
    
    def __qualität_profitabilität_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"quality",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][1]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][1]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][1]['children'][2]['value']
                
                json_column_1 = json['data']['score']['children'][1]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][1]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][1]['children'][2]['name']
                
                array_data = np.array([json_data_1, json_data_2, json_data_3])
                array_index = np.array([json_column_1, json_column_2, json_column_3])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Profitabilität / Rentabilität ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__profitabilität_df = df
    
        return self.__profitabilität_df
    
    def __qualität_kursentwicklung_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"quality",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][2]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][2]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][2]['children'][2]['value']
                
                json_column_1 = json['data']['score']['children'][2]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][2]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][2]['children'][2]['name']
                
                array_data = np.array([json_data_1, json_data_2, json_data_3])
                array_index = np.array([json_column_1, json_column_2, json_column_3])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Kursentwicklung und Volatilität ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__kursentwicklung_df = df
    
        return self.__kursentwicklung_df
    
    def __qualität_sicherheit_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"quality",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][3]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][3]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][3]['children'][2]['value']
                
                json_column_1 = json['data']['score']['children'][3]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][3]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][3]['children'][2]['name']
                
                array_data = np.array([json_data_1, json_data_2, json_data_3])
                array_index = np.array([json_column_1, json_column_2, json_column_3])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Sicherheit und Bilanz ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__sicherheit_df = df
    
        return self.__sicherheit_df
    
    # Get Dividenden-Check
    # https://aktie.traderfox.com/ajax/getStockTDFScore.php
    # Funktioniert
    def __dividend_rendite_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"dividend",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][0]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][0]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][0]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][0]['children'][3]['value']
                
                json_column_1 = json['data']['score']['children'][0]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][0]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][0]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][0]['children'][3]['name']
                
                array_data = np.array([json_data_1, json_data_2, json_data_3, json_data_4])
                array_index = np.array([json_column_1, json_column_2, json_column_3, json_column_4])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Dividenden-Rendite ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__div_rend_df = df
    
        return self.__div_rend_df
    
    def __dividend_kontinuität_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"dividend",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][1]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][1]['children'][1]['value']
                
                json_column_1 = json['data']['score']['children'][1]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][1]['children'][1]['name']
                
                array_data = np.array([json_data_1, json_data_2])
                array_index = np.array([json_column_1, json_column_2])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Dividenden-Kontinuität ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__div_kont_df = df
    
        return self.__div_kont_df
    
    def __dividend_wachstum_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"dividend",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][2]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][2]['children'][1]['value']
                
                json_column_1 = json['data']['score']['children'][2]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][2]['children'][1]['name']
                
                array_data = np.array([json_data_1, json_data_2])
                array_index = np.array([json_column_1, json_column_2])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Wachstum ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__div_wachs_df = df
    
        return self.__div_wachs_df
    
    def __dividend_qualität_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"dividend",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][3]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][3]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][3]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][3]['children'][3]['value']
                
                json_column_1 = json['data']['score']['children'][3]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][3]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][3]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][3]['children'][3]['name']
                
                array_data = np.array([json_data_1, json_data_2, json_data_3, json_data_4])
                array_index = np.array([json_column_1, json_column_2, json_column_3, json_column_4])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Qualität des Unternehmens ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__div_qual_df = df
    
        return self.__div_qual_df
    
    # Get Wachstums-Check
    # https://aktie.traderfox.com/ajax/getStockTDFScore.php
    # Funktioniert
    def __wachstum_wachstum_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"growth",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][0]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][0]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][0]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][0]['children'][3]['value']
                json_data_5 = json['data']['score']['children'][0]['children'][4]['value']
                json_data_6 = json['data']['score']['children'][0]['children'][5]['value']
                
                json_column_1 = json['data']['score']['children'][0]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][0]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][0]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][0]['children'][3]['name']
                json_column_5 = json['data']['score']['children'][0]['children'][4]['name']
                json_column_6 = json['data']['score']['children'][0]['children'][5]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3, json_data_4,
                                       json_data_5, json_data_6])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3, json_column_4,
                                        json_column_5, json_column_6])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Wachstum ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__grow_wachs_df = df
    
        return self.__grow_wachs_df
    
    def __wachstum_trend_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"growth",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][1]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][1]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][1]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][1]['children'][3]['value']
                json_data_5 = json['data']['score']['children'][1]['children'][4]['value']
                
                json_column_1 = json['data']['score']['children'][1]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][1]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][1]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][1]['children'][3]['name']
                json_column_5 = json['data']['score']['children'][1]['children'][4]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3, json_data_4,
                                       json_data_5])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3, json_column_4,
                                        json_column_5])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Trend ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__grow_trend_df = df
    
        return self.__grow_trend_df
    
    def __wachstum_finanzierbarkeit_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"growth",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][2]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][2]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][2]['children'][2]['value']
                
                json_column_1 = json['data']['score']['children'][2]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][2]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][2]['children'][2]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Finanzierbarkeit Wachstum ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__grow_finanz_df = df
    
        return self.__grow_finanz_df
    
    # Get Robustheits-Check
    # https://aktie.traderfox.com/ajax/getStockTDFScore.php
    # Funktioniert
    def __robustheits_performance_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"the_big_call",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][0]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][0]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][0]['children'][2]['value']
                
                json_column_1 = json['data']['score']['children'][0]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][0]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][0]['children'][2]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Performance ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__robu_perf_df = df
    
        return self.__robu_perf_df
    
    def __robustheits_volatilität_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"the_big_call",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][1]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][1]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][1]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][1]['children'][3]['value']
                
                json_column_1 = json['data']['score']['children'][1]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][1]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][1]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][1]['children'][3]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3, json_data_4])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3, json_column_4])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Volatilität ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__robu_vola_df = df
    
        return self.__robu_vola_df
    
    def __robustheits_drawdown_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"the_big_call",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][2]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][2]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][2]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][2]['children'][3]['value']
                
                json_column_1 = json['data']['score']['children'][2]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][2]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][2]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][2]['children'][3]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3, json_data_4])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3, json_column_4])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['DrawDown ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__robu_drawdown_df = df
    
        return self.__robu_drawdown_df

    def __robustheits_robustheit_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                "score" :	"the_big_call",
                "get_score_warnings" :	"true"
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockTDFScore.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                json_data_1 = json['data']['score']['children'][3]['children'][0]['value']
                json_data_2 = json['data']['score']['children'][3]['children'][1]['value']
                json_data_3 = json['data']['score']['children'][3]['children'][2]['value']
                json_data_4 = json['data']['score']['children'][3]['children'][3]['value']
                
                json_column_1 = json['data']['score']['children'][3]['children'][0]['name']
                json_column_2 = json['data']['score']['children'][3]['children'][1]['name']
                json_column_3 = json['data']['score']['children'][3]['children'][2]['name']
                json_column_4 = json['data']['score']['children'][3]['children'][3]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3, json_data_4])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3, json_column_4])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['Robustheit in Abwärtsphasen ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__robu_robustheit_df = df
    
        return self.__robu_robustheit_df
    
    # Get Scoring System
    # https://aktie.traderfox.com/ajax/getStockScoringSystems.php
    def __scoring_high_growth_investing_df(self):
        # -- create session ---
        session = requests.session()
        session.headers.update(self.__headers_standard)
        
        url = f"https://aktie.traderfox.com/visualizations/{self.ticker}"
        page = session.get(url)
        
        if page.text.find('stock_id-') != -1:
            table_int = page.text.find('stock_id-')
            stock_id = page.text[table_int+9:table_int+20].split('/')[0]

            data = {
                "stock_id" : stock_id,
                    }
            
            url = 'https://aktie.traderfox.com/ajax/getStockScoringSystems.php'
                   
            page = session.post(url, data=data)
            
            json = page.json()
            
            if len(json['data']) == 4:
                #High-Growth-Investing-Score
                json_data_1 = json['data']['scoring_hgi']['children'][0]['children'][0]['value']
                json_data_2 = json['data']['scoring_hgi']['children'][1]['children'][0]['value']
                json_data_3 = json['data']['scoring_hgi']['children'][2]['children'][0]['value']
                json_data_4 = json['data']['scoring_hgi']['children'][3]['children'][0]['value']
                json_data_5 = json['data']['scoring_hgi']['children'][4]['children'][0]['value']
                json_data_6 = json['data']['scoring_hgi']['children'][5]['children'][0]['value']
                
                json_column_1 = json['data']['scoring_hgi']['children'][0]['name']
                json_column_2 = json['data']['scoring_hgi']['children'][1]['name']
                json_column_3 = json['data']['scoring_hgi']['children'][2]['name']
                json_column_4 = json['data']['scoring_hgi']['children'][3]['name']
                json_column_5 = json['data']['scoring_hgi']['children'][4]['name']
                json_column_6 = json['data']['scoring_hgi']['children'][5]['name']
                
                array_data = np.array([json_data_1, json_data_2, 
                                       json_data_3, json_data_4,
                                       json_data_5, json_data_6])
                
                array_index = np.array([json_column_1, json_column_2,
                                        json_column_3, json_column_4,
                                        json_column_5, json_column_6])
                
                df = pd.DataFrame(array_data, 
                                  index = array_index,
                                  columns = ['High-Growth-Investing-Score ' + self.ticker]
                                  )
            else:
                df = None
        else:
            df = None
            
        self.__piotroski_df = df
    
        return self.__piotroski_df
        
#print(umsatzwachstum_5y('US0378331005'))
    
'''
# Funktioniert
# Get Scoring System
# https://aktie.traderfox.com/ajax/getStockScoringSystems.php

def umsatzwachstum_10y(isin):
    # -- create session ---
    
    session = requests.session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    # set headers for all requests
    session.headers.update(headers)
    
    # --- get cookies ---
    
    url = f"https://aktie.traderfox.com/visualizations/{isin}"
    page = session.get(url)
    #print(page.text)
    
    if page.text.find('stock_id-') != -1:
        table_int = page.text.find('stock_id-')
        #stock_id = page.text[table_int+9:790].split('/')[0]
    
        stock_id = page.text[table_int+9:table_int+20].split('/')[0]
        #print(table_int)
        #print(stock_id)
        
        # --- search ---
        
        #data = {
        #    "stock_id" : '8590335'
        #        }
        data = {
            "stock_id" : stock_id
                }
        
        
        url = 'https://aktie.traderfox.com/ajax/getStockScoringSystems.php'
        
        
        page = session.post(url, data=data)
        
        #print(page.text)
        
        json = page.json()
        
        if len(json['data']) == 4:
            json = json['data']['scoring_aaqs']['children'][0]['children'][0]
            json = json['value']
            
            if json == 'null':
                json = None
        else:
            json = None
    else:
        json = None
    
    return json

print(umsatzwachstum_10y('US0378331005'))
'''












