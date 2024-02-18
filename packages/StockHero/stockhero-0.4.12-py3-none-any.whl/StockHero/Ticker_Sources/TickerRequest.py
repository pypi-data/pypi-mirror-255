# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 09:17:42 2022

@author: RobWen
Version: 0.4.0
"""

class TickerRequest:
    def __init__(self, ticker, headers_standard):
        self.ticker = ticker
        #self.headers_standard = headers_standard

    def __repr__(self):
        return (self.ticker)

    def __str__(self):
        return (self.ticker)
        # return(self.Morningstar_Key_Ratios or '') # by None