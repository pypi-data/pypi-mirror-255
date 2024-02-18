# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 18:02:49 2022

@author: RobWen
Version: 0.4.5
"""

# Packages
from StockHero.Ticker_Sources.GuruFocusRequest import *
from StockHero.Ticker_Sources.MorningStarRequest import *
from StockHero.Ticker_Sources.NASDAQRequest import *
from StockHero.Ticker_Sources.StratosphereRequest import *
from StockHero.Ticker_Sources.TraderFoxRequest import *
from StockHero.Ticker_Sources.YahooRequest import *

    ##############
    ###        ###
    ###  Data  ###
    ###        ###
    ##############

class Ticker:
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.__headers_standard = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}
        self.gurufocus = GuruFocusRequest(ticker = self.ticker, headers_standard = self.__headers_standard)
        self.morningstar = MorningStarRequest(ticker = self.ticker, headers_standard = self.__headers_standard)
        self.nasdaq = NASDAQRequest(ticker = self.ticker, headers_standard = self.__headers_standard)
        self.stratosphere = StratosphereRequest(ticker = self.ticker, headers_standard = self.__headers_standard)
        self.traderfox = TraderFoxRequest(ticker = self.ticker, headers_standard = self.__headers_standard)
        self.yahoo = YahooRequest(ticker = self.ticker, headers_standard = self.__headers_standard)
    
    def __repr__(self):
        return(self.ticker)
        
    def __str__(self):
        return(self.ticker)
        #return(self.ticker or '') # by None

###############################################################################
###############################################################################