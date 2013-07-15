import pandas 
from qstkutil import DataAccess as da
import numpy as np
import math
import copy
import qstkutil.qsdateutil as du
import datetime as dt
import qstkutil.DataAccess as da
import qstkutil.tsutil as tsu
import qstkstudy.EventProfiler as ep
import csv

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

# Get the data from the data store
storename = "Yahoo" # get data from daily prices source

# Available field names: open, close, high, low, close, actual_close, volume
closefield = "actual_close"
volumefield = "volume"
window = 10

def findEvents(symbols, startday,endday, marketSymbol,verbose=False):

	# Reading the Data for the list of Symbols.	
	timeofday=dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(startday,endday,timeofday)
	dataobj = da.DataAccess(storename)
	if verbose:
            print __name__ + " reading data"
	# Reading the Data
	close = dataobj.get_data(timestamps, symbols, closefield)
	
	# Completing the Data - Removing the NaN values from the Matrix
	#close = (close.fillna(method='ffill')).fillna(method='backfill')

	if verbose:
            print __name__ + " finding events"

	# Generating the orders
	# Event described is : when the actual close of the stock price drops below $5.00

	f = open('orders.csv', 'wt')
	writer = csv.writer(f)

	for symbol in symbols:
		
		for i in range(2,len(close[symbol])):
			if close[symbol][i-1] >=5.0 and close[symbol][i] < 5.0 : 
				writer.writerow( (close.index[i].year, close.index[i].month, close.index[i].day, symbol, 'BUY', 100) )

				j = i + 5
				if (j > len(close[symbol])) : 
					j = len(close[ysmbol])

				writer.writerow( (close.index[j].year, close.index[j].month, close.index[j].day, symbol, 'SELL', 100) )
	f.close()


#################################################
################ MAIN CODE ######################
#################################################

dataobj = da.DataAccess(storename)
symbols = dataobj.get_symbols_from_list("sp5002012")
#symbols.append('SPY')

startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
findEvents(symbols,startday,endday,marketSymbol='SPY',verbose=True)

#eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=20,lookforward_days=20,verbose=True)

#eventProfiler.study(filename="MyEventStudy2.pdf",plotErrorBars=True,plotMarketNeutral=False,plotEvents=False,marketSymbol='SPY')


