import pandas 
import numpy as np
import math
import copy
import qstkutil.qsdateutil as du
import datetime as dt
import qstkutil.DataAccess as da
import qstkutil.tsutil as tsu
import qstkstudy.EventProfiler as ep
from optparse import OptionParser
from sys import exit
import os
from operator import itemgetter

parser = OptionParser()
    
# parser.parse_args() returns a tuple of (options, args)
# As of right now, we don't have any options for our program, so we only care about the three arguments:
# cash, input file, output file
args = parser.parse_args()[1]
    
if len(args) != 3:
	print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING."
        exit()

try:
	startcash = float(args[0])
except ValueError:
	print "ARGUMENT FOR CASH IS NOT A FLOAT!"

listOfOrdersFile = str(args[1])
if not (os.path.exists(listOfOrdersFile)):
	print "File containing list of orders does not exist."
	raise ValueError
		
trades = np.loadtxt(listOfOrdersFile,
        dtype='i4,i2,i2,S4,S4,i4',
        delimiter=',', 
       )

trades = sorted(trades, key=itemgetter(0, 1, 2))

tradesymbols = []
tradedates = []
for i in trades:
    tradesymbols.append(i[3])
    tradedates.append(dt.datetime(i[0], i[1], i[2], 16))

tradesymbolsnodups = list(set(tradesymbols))

startday = tradedates[0]
endday = tradedates[len(tradedates) - 1]
timeofday = dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

dataobj = da.DataAccess("Yahoo")
close = dataobj.get_data(timestamps,tradesymbolsnodups,"close")

casharray = []
currentcash = startcash

for index, ts in enumerate(timestamps):
    i = -1
    try:
        while 1:
            i = tradedates.index(ts, i+1)
	    symbol = trades[i][3]
	    price = close.ix[index][symbol]
	    action = trades[i][4]
	    numshares = trades[i][5]
	    extended = price * numshares
	    if (action == "Sell"):
		    extended *= -1
	    currentcash -= extended
    except ValueError:
	    pass
    casharray.append((ts, currentcash))

ownedarray=[]
holdings = {}

for index, ts in enumerate(timestamps):
    i = -1
    try:
        while 1:
            i = tradedates.index(ts, i+1)
	    symbol = trades[i][3]
	    action = trades[i][4]
	    numshares = trades[i][5]
	    if (action == "SELL"):
		    numshares *= -1
	    holdings[symbol] = holdings.get(symbol, 0) + numshares
	    #print ownedarray
    except ValueError:
	    pass
    ownedarray.append((ts, currentaapl, currentgoog, currentibm, currentxom))

valuesarray = []

for index, owned in enumerate(ownedarray):
	priceaapl = close.ix[index]['AAPL']
	pricegoog = close.ix[index]['GOOG']
	priceibm = close.ix[index]['IBM']
	pricexom = close.ix[index]['XOM']

	extended = owned[1] * priceaapl + owned[2] * pricegoog + owned[3] * priceibm + owned[4] * pricexom
	extended += casharray[index][1]

	valuesarray.append((owned[0], extended))

print valuesarray
