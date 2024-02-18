# -*- coding: utf-8 -*-
"""
Created on Fri Aug 06 22:46:42 2023

@author: RobWen
Version: 0.4.4
"""

# Packages
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

# Header
from .TickerRequest import *

class MorningStarRequest(TickerRequest):
    def __init__(self, ticker, headers_standard):
        super().__init__(ticker, headers_standard)
        self.__headers_standard = headers_standard

    ################################
    ###                          ###
    ###   Morningstar Requests   ###
    ###                          ###
    ################################

    @property
    def quote(self):
        return self.__morningstar_quote_abfrage()

    @property
    def key_statistics(self):
        return self.__morningstar_quote_abfrage_key_statistics()

    @property
    def growth_rev(self):
        return self.__morningstar_quote_abfrage_growth_revenue()
    
    @property
    def growth_op_inc(self):
        return self.__morningstar_quote_abfrage_operating_income()
    
    @property
    def growth_net_inc(self):
        return self.__morningstar_quote_abfrage_net_income()
    
    @property
    def growth_eps(self):
        return self.__morningstar_quote_abfrage_growth_eps()
    
    ##########################
    ###                    ###
    ###  Morningstar Data  ###
    ###                    ###
    ##########################
    
    # Dummy Abfragen, um Fehler im Vorfeld abzufangen
    def __morningstar_quote_abfrage(self):
        
        ' Dummy Abfrage'
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__morningstar_quote_df()
    
    # Führt eine Abfrage durch um die Performance ID zu finden 
    def __morningstar_performance_id(self):
        url = "https://www.morningstar.co.uk/uk/funds/SecuritySearchResults.aspx"
        params = {'search': f'{self.ticker}'}
        
        data = requests.get(url, params=params, headers = self.__headers_standard)
        data = BeautifulSoup(data.content, 'html.parser')
        
        try:
            performance_id = data.find('td', {'class':'msDataText searchLink'})
            self.name_id = performance_id.text
            performance_id = performance_id.prettify().split()[4].split('=')[2].split(']')[0]
        except:
            return None
        
        return performance_id
    
    ### Morningstar Quote                                       ###
    ### e.g. https://www.morningstar.com/stocks/xnas/nvda/quote ###
    ### Rückgabe None implementiert und getestet                ###
    ### Ungültige Werte = NaN implementiert                     ###
    def __morningstar_quote_df(self):
        morningstar_performance_id = self.__morningstar_performance_id()
        
        if morningstar_performance_id is None:
            return None
        else:
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/header/v2/data/{morningstar_performance_id}/securityInfo?showStarRating=&languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.69.0'
            
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            dictionary = r.json()
            
            priceEarnings = dictionary["priceEarnings"]
            priceBook = dictionary["priceBook"]
            priceSale = dictionary["priceSale"]
            forwardPE = dictionary["forwardPE"]
            forwardDivYield = dictionary["forwardDivYield"]
            
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/{morningstar_performance_id}?languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.69.0'
            
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            json = r.json()
            
            revenue3YearGrowth = json['revenue3YearGrowth']['stockValue']
            netIncome3YearGrowth = json['netIncome3YearGrowth']['stockValue']
            operatingMarginTTM = json['operatingMarginTTM']['stockValue']
            netMarginTTM = json['netMarginTTM']['stockValue']
            roaTTM = json['roaTTM']['stockValue']
            roeTTM = json['roeTTM']['stockValue']
            freeCashFlowTTM = json['freeCashFlow']['cashFlowTTM']
            
            try:
                priceEarnings = '{:.2f}'.format(float(priceEarnings))
                priceBook = '{:.2f}'.format(float(priceBook))
                priceSale = '{:.2f}'.format(float(priceSale))
                forwardPE = '{:.2f}'.format(float(forwardPE))
                forwardDivYield = float(forwardDivYield) * 100 # in %
                revenue3YearGrowth = '{:.2f}'.format(float(revenue3YearGrowth))
                netIncome3YearGrowth = '{:.2f}'.format(float(netIncome3YearGrowth))
                operatingMarginTTM = '{:.2f}'.format(float(operatingMarginTTM))
                netMarginTTM = '{:.2f}'.format(float(netMarginTTM))
                roaTTM = '{:.2f}'.format(float(roaTTM))
                roeTTM = '{:.2f}'.format(float(roeTTM))
                freeCashFlowTTM = '{:,.2f}'.format(float(freeCashFlowTTM)) # locale='en_US'
            except(TypeError):
                pass
            
            df_morningstar_quote = pd.DataFrame([priceEarnings, priceBook, priceSale, forwardPE, forwardDivYield
                               , revenue3YearGrowth, netIncome3YearGrowth, operatingMarginTTM, netMarginTTM, roaTTM, roeTTM
                               , freeCashFlowTTM]
                              , index =['Price/Earnings', 'Price/Book', 'Price/Sales', 'Consensus Forward P/E', 'Forward Div Yield %'
                                        , 'Rev 3-Yr Growth', 'Net Income 3-Yr Growth'
                                        , 'Operating Margin % TTM', 'Net Margin % TTM', 'ROA % TTM'
                                        , 'ROE % TTM', 'Current Free Cash Flow']
                              , columns =[self.ticker + ' Ratio'])
            
            df_morningstar_quote = df_morningstar_quote.fillna(value=np.nan) # None mit NaN ersetzen für df
        
        return df_morningstar_quote
    
    # Dummy Abfragen, um Fehler im Vorfeld abzufangen
    
    def __morningstar_quote_abfrage_key_statistics(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__morningstar_key_statistics_df()
    
    def __morningstar_quote_abfrage_growth_revenue(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__morningstar_growth_revenue_df()
    
    def __morningstar_quote_abfrage_operating_income(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__morningstar_operating_income_df()
    
    def __morningstar_quote_abfrage_net_income(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__morningstar_net_income_df()
    
    def __morningstar_quote_abfrage_growth_eps(self):
        
        if self.ticker is None or self.ticker == '':
            self.ticker = 'None'
            return None
        
        return self.__morningstar_growth_eps_df()
    
    # Eigentlichen Abfragen
    
    # Wird zur Generierung der Key Statistics verwendet
    def __initialize_dataframe(self, columns, index):
        df = pd.DataFrame([[''] * len(columns)], columns=columns, index=index)
        return df
    
    def __morningstar_key_statistics_df(self):
        morningstar_performance_id = self.__morningstar_performance_id()
        
        if morningstar_performance_id is None:
            return None
        else:
            df1 = self.__morningstar_quote_abfrage_growth_revenue()
            df2 = self.__morningstar_quote_abfrage_operating_income()
            df3 = self.__morningstar_quote_abfrage_net_income()
            df4 = self.__morningstar_quote_abfrage_growth_eps()
            
            df1_1 = self.__initialize_dataframe(df1.columns, ['Growth Revenue %'])
            df2_1 = self.__initialize_dataframe(df2.columns, ['Operating Income %'])
            df3_1 = self.__initialize_dataframe(df3.columns, ['Net Income %'])
            df4_1 = self.__initialize_dataframe(df4.columns, ['EPS %'])
            
            morningstar_key_statistics_df = pd.concat([df1_1, df1, df2_1, df2 ,df3_1, df3, df4_1, df4], axis=0)
        return morningstar_key_statistics_df
    
    def __morningstar_growth_revenue_df(self):
        morningstar_performance_id = self.__morningstar_performance_id()
        
        if morningstar_performance_id is None:
            return None
        else:
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/growthTable/{morningstar_performance_id}?languageId=en&locale=en&clientId=undefined&component=sal-components-key-stats-growth-table&version=3.71.0'
    
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            json = r.json()
            
            columns = []
            for i in range(len(json['dataList'])):
                columns.append(json['dataList'][i]['fiscalPeriodYearMonth'])
                
            liste_values = []
            for i in range(len(json['dataList'])):
                liste_values.append(list(json['dataList'][i]['revenuePer'].values()))
                
            array_table = np.array(liste_values).transpose()
            
            morningstar_growth_revenue_df = pd.DataFrame(array_table
                               , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                               , columns = columns
                               )
            
            # Leere Zellen mit NaN auffüllen
            # Werte auf die 2te Nachkommastelle runden
            # Wie bei Morningstar dargestellt, ansonsten gibt es beim späteren Umwandeln in Markdown Probleme
            morningstar_growth_revenue_df = morningstar_growth_revenue_df.fillna(value=np.nan).round(2)
        
        return morningstar_growth_revenue_df
    
    def __morningstar_operating_income_df(self):
        morningstar_performance_id = self.__morningstar_performance_id()
        
        if morningstar_performance_id is None:
            return None
        else:
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/growthTable/{morningstar_performance_id}?languageId=en&locale=en&clientId=undefined&component=sal-components-key-stats-growth-table&version=3.71.0'
    
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            json = r.json()
            
            columns = []
            for i in range(len(json['dataList'])):
                columns.append(json['dataList'][i]['fiscalPeriodYearMonth'])
                
            liste_values = []
            for i in range(len(json['dataList'])):
                liste_values.append(list(json['dataList'][i]['operatingIncome'].values()))
                
            array_table = np.array(liste_values).transpose()
            
            morningstar_operating_income_df = pd.DataFrame(array_table
                               , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                               , columns = columns
                               )
            
            # Leere Zellen mit NaN auffüllen
            # Werte auf die 2te Nachkommastelle runden
            # Wie bei Morningstar dargestellt, ansonsten gibt es beim späteren Umwandeln in Markdown Probleme
            morningstar_operating_income_df = morningstar_operating_income_df.fillna(value=np.nan).round(2)
        
        return morningstar_operating_income_df
    
    def __morningstar_net_income_df(self):
        morningstar_performance_id = self.__morningstar_performance_id()
        
        if morningstar_performance_id is None:
            return None
        else:
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/growthTable/{morningstar_performance_id}?languageId=en&locale=en&clientId=undefined&component=sal-components-key-stats-growth-table&version=3.71.0'
    
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            json = r.json()
            
            columns = []
            for i in range(len(json['dataList'])):
                columns.append(json['dataList'][i]['fiscalPeriodYearMonth'])
                
            liste_values = []
            for i in range(len(json['dataList'])):
                liste_values.append(list(json['dataList'][i]['netIncomePer'].values()))
                
            array_table = np.array(liste_values).transpose()
            
            morningstar_net_income_df = pd.DataFrame(array_table
                               , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                               , columns = columns
                               )
            
            # Leere Zellen mit NaN auffüllen
            # Werte auf die 2te Nachkommastelle runden
            # Wie bei Morningstar dargestellt, ansonsten gibt es beim späteren Umwandeln in Markdown Probleme
            morningstar_net_income_df = morningstar_net_income_df.fillna(value=np.nan).round(2)
        
        return morningstar_net_income_df
    
    def __morningstar_growth_eps_df(self):
        morningstar_performance_id = self.__morningstar_performance_id()
        
        if morningstar_performance_id is None:
            return None
        else:
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/growthTable/{morningstar_performance_id}?languageId=en&locale=en&clientId=undefined&component=sal-components-key-stats-growth-table&version=3.71.0'
    
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            json = r.json()
            
            columns = []
            for i in range(len(json['dataList'])):
                columns.append(json['dataList'][i]['fiscalPeriodYearMonth'])
                
            liste_values = []
            for i in range(len(json['dataList'])):
                liste_values.append(list(json['dataList'][i]['epsPer'].values()))
                
            array_table = np.array(liste_values).transpose()
            
            morningstar_growth_eps_df = pd.DataFrame(array_table
                               , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                               , columns = columns
                               )
            
            # Leere Zellen mit NaN auffüllen
            # Werte auf die 2te Nachkommastelle runden
            # Wie bei Morningstar dargestellt, ansonsten gibt es beim späteren Umwandeln in Markdown Probleme
            morningstar_growth_eps_df = morningstar_growth_eps_df.fillna(value=np.nan).round(2)
        
        return morningstar_growth_eps_df