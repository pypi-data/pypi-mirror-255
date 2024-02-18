#  ______     __                          __        __    __                               
# /      \   |  \                        |  \      |  \  |  \                              
#|  $$$$$$\ _| $$_     ______    _______ | $$   __ | $$  | $$  ______    ______    ______  
#| $$___\$$|   $$ \   /      \  /       \| $$  /  \| $$__| $$ /      \  /      \  /      \ 
# \$$    \  \$$$$$$  |  $$$$$$\|  $$$$$$$| $$_/  $$| $$    $$|  $$$$$$\|  $$$$$$\|  $$$$$$\
# _\$$$$$$\  | $$ __ | $$  | $$| $$      | $$   $$ | $$$$$$$$| $$    $$| $$   \$$| $$  | $$
#|  \__| $$  | $$|  \| $$__/ $$| $$_____ | $$$$$$\ | $$  | $$| $$$$$$$$| $$      | $$__/ $$
# \$$    $$   \$$  $$ \$$    $$ \$$     \| $$  \$$\| $$  | $$ \$$     \| $$       \$$    $$
#  \$$$$$$     \$$$$   \$$$$$$   \$$$$$$$ \$$   \$$ \$$   \$$  \$$$$$$$ \$$        \$$$$$$ 

__title__ = 'StockHero'
__description__ = 'stock market data downloader'
__url__ = 'https://github.com/RobWen/StockHero'
__version__ = '0.4.12'
__author__ = 'RobWen'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2022 - 2024'
__thanks__ = 'Thanks to my colleagues @Fraunhofer IIS (Tommy and Tim)'

'''
Release History
0.4.12 (09.02.2024)
    - Stratosphere Bug Fix

0.4.11 (28.12.2023)
    - Stratosphere Bug Fix

0.4.10 (14.09.2023)
    - Gurufocus Dividend Yield eingeführt

0.4.9 (02.09.2023)
    - Readme überarbeitet
    - Gurufocus PE Ratio überarbeitet (MMM, IFF, OTLY)
    - Yahoo statistics_p rausgeworfen
    - Suche bei Stratosphere eingeführt und der Name wird auch ausgegeben
        - damit kann die GUI nochmal überarbeiten werden

0.4.8 (28.08.2023)
    - added Dependencies
    - added Fear_and_Greed - API
    
0.4.7 (24.08.2023)
    - changed Badge
    - Stratosphere Summary more features
    
0.4.6 (22.08.2023)
    - changed required Python Version

0.4.5 (19.08.2023)
    - added Stratosphere Summary
    - minor fixes gurufocus

0.4.4 (16.08.2023)
    - minor fixes morningstar

0.4.3 (15.08.2023)
    - minor fixes gurufocus

0.4.2 (08.08.2023)
    - minor fixes morningstar

0.4.1 (02.11.2022)
    - added Traderfox

0.4.0 (26.08.2022)
    - introducing a new architecture (again ^^)

0.3.3 (06.07.2022)
    - Some Morningstar Features are up and running again
    - Morningstar is now also working with ISIN

0.3.2 (27.06.2022)
    - Yahoo Finance now able to handle ISIN

0.3.1 (25.06.2022)
    - introducing a new architecture

0.2.10 (xx.06.2022)
    - minor fixes (Morningstar Quote)

0.2.9 (15.06.2022)
    - minor fixes (Fear and Greed Index)

0.2.8 (05.06.2022)
    - minor fixes

0.2.7 (09.12.2021)
    - added some indizies (Dax, MDax, Euro Stoxx 50, Dow Jones, Nasdaq etc.) from Börse Hamburg / Hannover
    - added Debt-to-EBITDA from Gurufocus
    - fixed some bugs

0.2.6 (22.11.2021)
    - added the Fear and Greed Index from CNN
    - added Historical PE-Ratio from Gurufocus
    - optimised NASDAQ summary, looks much nicer now
    - optimised Morningstar Quote, now also NYSE listed stocks work

0.2.5 (29.10.2021)
    - combined nasdaq_pe_forecast / nasdaq_gr_forecast / nvda.nasdaq_peg_forecast (MultiIndex)
    - added yahoo_statistics_p (a bit of PreProcessing)
    - code cleanup
    - np.NaN for any not valid value
    - None for any empty pd.dataframe
'''