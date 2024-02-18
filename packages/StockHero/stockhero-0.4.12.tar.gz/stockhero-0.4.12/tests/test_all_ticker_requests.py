# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 12:45:49 2022

@author: RobWen
Version: 0.4.0
"""

import StockHero as stock
import time


'''  create TICKER for Nvidia stock  '''
ticker_creation_start = time.time()

nvda = stock.Ticker('NVDA')                    # e.g. NVIDIA Corp

ticker_creation_end = time.time()
ticker_creation_time = ticker_creation_end - ticker_creation_start
print("[TIME]:\tTicker creation:\t\t{:5.3f}ms".format(ticker_creation_time * 1e3))



'''  test all MorningStar requests  '''
morningstar_request_start = time.time()

print(nvda.morningstar.quote)                  # Quote
print(nvda.morningstar.growth_rev)             # Growth - Revenue %
print(nvda.morningstar.growth_op_inc)          # Growth - Operating Income %
print(nvda.morningstar.growth_net_inc)         # Growth - Net Income %
print(nvda.morningstar.growth_eps)             # Growth - EPS %

morningstar_request_end = time.time()
morningstar_request_time = morningstar_request_end - morningstar_request_start
print("[TIME]:\tMorningStar request:\t{:5.3f}ms".format(morningstar_request_time * 1e3))



'''  test all Yahoo Finance requests  '''
yahoo_request_start = time.time()

print(nvda.yahoo.statistics)                   # Statistics
#print(nvda.yahoo.statistics_p)                # Statistics - PreProcessed

yahoo_request_end = time.time()
yahoo_request_time = yahoo_request_end - yahoo_request_start
print("[TIME]:\tYahoo request:\t\t{:5.3f}ms".format(yahoo_request_time * 1e3))



'''  test all NASDAQ requests  '''
nasdaq_request_start = time.time()

print(nvda.nasdaq.summ)                        # Summary
print(nvda.nasdaq.div_hist)                    # Dividend History
print(nvda.nasdaq.hist_quotes_stock)           # Historical Quotes for Stocks
print(nvda.nasdaq.hist_quotes_etf)             # Historical Quotes for ETFs
print(nvda.nasdaq.hist_nocp)                   # Historical Nasdaq Official Closing Price (NOCP)
print(nvda.nasdaq.fin_income_statement_y)      # Financials - Income Statement - Yearly
print(nvda.nasdaq.fin_balance_sheet_y)         # Financials - Balance Sheet    - Yearly
print(nvda.nasdaq.fin_cash_flow_y)             # Financials - Cash Flow        - Yearly
print(nvda.nasdaq.fin_fin_ratios_y)            # Financials - Financial Ratios - Yearly
print(nvda.nasdaq.fin_income_statement_q)      # Financials - Income Statement - Quarterly
print(nvda.nasdaq.fin_balance_sheet_q)         # Financials - Balance Sheet    - Quarterly
print(nvda.nasdaq.fin_cash_flow_q)             # Financials - Cash Flow        - Quarterly
print(nvda.nasdaq.fin_fin_ratios_q)            # Financials - Financial Ratios - Quarterly
print(nvda.nasdaq.earn_date_eps)               # Earnings Date - Earnings Per Share
print(nvda.nasdaq.earn_date_surprise)          # Earnings Date - Quarterly Earnings Surprise Amount
print(nvda.nasdaq.yearly_earn_forecast)        # Earnings Date - Yearly Earnings Forecast
print(nvda.nasdaq.quarterly_earn_forecast)     # Earnings Date - Quarterly Earnings Forecast
print(nvda.nasdaq.pe_peg_forecast)             # Price/Earnings, PEG Ratios, Growth Rates Forecast

nasdaq_request_end = time.time()
nasdaq_request_time = nasdaq_request_end - nasdaq_request_start
print("[TIME]:\tNASDAQ request:\t\t{:5.3f}ms".format(nasdaq_request_time * 1e3))



'''  test all GuruFocus properties  '''
gurufocus_request_start = time.time()

print(nvda.gurufocus.pe_ratio_av)              # Historical Average Price/Earnings-Ratio
print(nvda.gurufocus.debt_to_ebitda)           # Debt-to-EBITDA Ratio

gurufocus_request_end = time.time()
gurufocus_request_time = gurufocus_request_end - gurufocus_request_start
print("[TIME]:\tGuruFocus request:\t\t{:5.3f}ms".format(gurufocus_request_time * 1e3))



'''  print time summary for single requests  '''
print("\n\n\n#####  TIME CONSUMPTION FOR SINGLE REQUESTS  #####")
print("[TIME]:\tTicker creation:\t\t{:9.3f}ms".format(ticker_creation_time * 1e3))
print("[TIME]:\tMorningStar request:\t{:9.3f}ms".format(morningstar_request_time * 1e3))
print("[TIME]:\tYahoo request:\t\t\t{:9.3f}ms".format(yahoo_request_time * 1e3))
print("[TIME]:\tNASDAQ request:\t\t\t{:9.3f}ms".format(nasdaq_request_time * 1e3))
print("[TIME]:\tGuruFocus request:\t\t{:9.3f}ms".format(gurufocus_request_time * 1e3))
print("\n[TIME]:\tTOTAL:\t\t\t\t\t{:9.3f}ms".format((ticker_creation_time + morningstar_request_time +
                                                   yahoo_request_time + nasdaq_request_time +
                                                   gurufocus_request_time) * 1e3))
