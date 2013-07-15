import datetime as dt
import qstkutil.qsdateutil as du

class StrategyData:
    def __init__(self, dataAccess, listOfStocks, startTime, endTime):

        self.dataAccess = dataAccess
       	timeofday=dt.timedelta(hours=16)
        self.timestampIndex = du.getNYSEdays(startTime,endTime,timeofday)
        self.symbolIndex = listOfStocks

        print __name__ + " reading data"

	# Reading the Data
	self.priceArray = dataAccess.get_data(self.timestampIndex, self.symbolIndex, "actual_close")

        self.prevTsIdx = 0

    def getPrice(self, timestamp, ticker, description):
        '''
        Returns a single price based on the parameters
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        NOTE: If the data is incorrect or invalid, the function will return None  
        '''

        return self.priceArray.ix[timestamp][ticker]

