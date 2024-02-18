# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 09:32:50 2022

@author: RobWen
Version: 0.4.10
"""

# Packages
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Header
from .TickerRequest import *

class GuruFocusRequest(TickerRequest):
    def __init__(self, ticker, headers_standard):
        super().__init__(ticker, headers_standard)
        self.__headers_standard = headers_standard

    ##############################
    ###                        ###
    ###  Gurufocus Requests    ###
    ###                        ###
    ##############################

    @property
    def pe_ratio_av(self):
        return self.__gurufocus_pe_ratio_av_v()

    @property
    def debt_to_ebitda(self):
        return self.__gurufocus_debt_to_ebitda()
    
    @property
    def div_yield_av(self):
        return self.__gurufocus_div_yield_av_v()
       
    ##########################
    ###                    ###
    ###  Gurufocus Data    ###
    ###                    ###
    ##########################
    
    """
    # Wird scheinbar nicht mehr benötigt
    
    def __stock_exchange(self):
        r = requests.get(f'https://www.gurufocus.com/stock/{self.ticker}/summary')
        stock_exchange = BeautifulSoup(r.content, 'html.parser')
        
        try:
            stock_exchange = stock_exchange.find('span', {'class':'t-label'}).text.split()[0]
        except:
            return None
        
        return stock_exchange
    """
    
    def __gurufocus_pe_ratio_av_v(self):
        #if self.__stock_exchange() != None:
            r = requests.get(f'https://www.gurufocus.com/term/pettm/{self.ticker}/PE-Ratio')
            page = BeautifulSoup(r.content, 'html.parser')
        
            table = page.find('div', {'class':'history_bar value'})
            
            try:
                table = table.find('strong').text.split()
                if len(table) == 8:
                    df = pd.DataFrame([table[1], table[3], table[5], table[7]]
                                        ,  columns=[f"{self.ticker}'s PE Ratio Range Over the Past 10 Years"]
                                        ,  index = [table[0], table[2], table[4], table[6]])
                    self.__PE_Ratio_Average = df
                if table[1] == "At":
                    df = pd.DataFrame([table[1] + " " + table[2], table[4], table[6], table[8] + " " + table[9]]
                                        ,  columns=[f"{self.ticker}'s PE Ratio Range Over the Past 10 Years"]
                                        ,  index = [table[0], table[3], table[5], table[7]])
                    self.__PE_Ratio_Average = df
                if len(table) == 12:
                    df = pd.DataFrame([table[1] + " " + table[2], table[4] + " " + table[5], table[7] + " " + table[8], 
                                       table[10] + " " + table[11]]
                                        ,  columns=[f"{self.ticker}'s PE Ratio Range Over the Past 10 Years"]
                                        ,  index = [table[0], table[3], table[6], table[9]])
                    self.__PE_Ratio_Average = df
                return self.__PE_Ratio_Average
            except:
                return None
        #else:
        #    return None
        
    def __gurufocus_debt_to_ebitda(self):
        #if self.__stock_exchange() != None:
          
            url = f'https://www.gurufocus.com/term/debt2ebitda/{self.ticker}/Debt-to-EBITDA'
            page = requests.get(url)
            page = BeautifulSoup(page.content, 'html.parser')

            table = page.find('div', {'class':'history_bar value'})

            try:
                table = table.find('strong').text.split()
                #debt_to_EBITDA = table[7]
                df = pd.DataFrame([table[1], table[3], table[5], table[7]]
                                    ,  columns=[f"{self.ticker}'s Debt-to-EBITDA Range Over the Past 10 Years "]
                                    ,  index = [table[0], table[2], table[4], table[6]])
                self.__debt_to_EBITDA = df
                
                #try:
                #    self.__debt_to_EBITDA = float(debt_to_EBITDA)
                #except:
                #    return '#'
                return self.__debt_to_EBITDA
            except (AttributeError):
                return None

    def __gurufocus_div_yield_av_v(self):
          
            url = f'https://www.gurufocus.com/term/yield/{self.ticker}/Dividend-Yield-Percentage'
            page = requests.get(url)
            page = BeautifulSoup(page.content, 'html.parser')

            table = page.find('div', {'class':'history_bar value'})

            try:
                table = table.find('strong').text.split()

                df = pd.DataFrame([table[1], table[3], table[5], table[7]]
                                    ,  columns=[f"{self.ticker}'s Dividend Yield % Range Over the Past 10 Years "]
                                    ,  index = [table[0], table[2], table[4], table[6]])
                self.__Div_Yield_Average = df
                
                return self.__Div_Yield_Average
            except (AttributeError):
                return None