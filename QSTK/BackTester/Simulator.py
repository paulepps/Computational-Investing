from optparse import OptionParser
import Portfolio, Position, Order
import StrategyData
from Strategies import dollarStrategy
import qstkutil.qsdateutil as du
import numpy as np
import datetime as dt
import time
from operator import itemgetter
from qstkutil import DataAccess as da
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

class Simulator():
    def __init__(self, cash):

        self.startTime = dt.datetime(2008,1,1,16)
        self.currTimestamp = self.startTime
        self.endTime = dt.datetime(2009,12,31,16)

        #starting portfolio, position, and order initializations
        self.portfolio = Portfolio.Portfolio(cash, {})
        self.position = Position.Position()
        self.order = Order.Order()

        dataobj = da.DataAccess("Yahoo")
        self.listOfStocks = dataobj.get_symbols_from_list("sp5002012")

        self.strategyData = StrategyData.StrategyData(dataobj, self.listOfStocks, self.startTime, self.endTime)

    def buyStock(self, newOrder):
        '''
        @summary: function takes in an instance of OrderDetails, executes the changes to the portfolio and adds the order to the order table
        @param newOrder: an instance of OrderDetails representing the new order
        @warning: The Order should not be added to the order table before calling this function
        '''
        ts = newOrder['timestamp']

        price = self.strategyData.getPrice(ts, newOrder['symbol'], 'actual_close')

        if price == None or np.isnan (price):
            if noisy:
                print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
            return None
        else: 
            checkAmount = newOrder['shares']
            cost = checkAmount * price

            newOrder['fill/timestamp'] = ts
            newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'BUY') else -newOrder['shares']
            newOrder['fill/cashChange'] = -price

            #add trade to portfolio
            self.portfolio.buyTransaction(newOrder)
            #add position
            self.position.addPosition(ts,newOrder['symbol'],newOrder['fill/quantity'],price)

        newOrder.update()
        self.order.order.flush()
        return price

    def sellStock(self,newOrder):
        '''
        @summary: function takes in an instance of OrderDetails, executes the changes to the portfolio and adds the order to the order table
        @param newOrder: an instance of OrderDetails representing the new order
        @warning: The Order should not be added to the order table before calling this function
        '''
        ts = newOrder['timestamp']

        price = self.strategyData.getPrice(ts, newOrder['symbol'], 'actual_close')

        if price == None or np.isnan (price):
            if noisy:
                print "Price data unavailable for",ts,newOrder['symbol']
            return None
        else:
            checkAmount = newOrder['shares']

            if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                #Not enough shares owned to sell requested amount
                print "Not enough shares owned to sell the requested amount"
                return None

            cost = checkAmount * price

            newOrder['fill/timestamp'] = ts
            newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares']
            newOrder['fill/cashChange'] = price

            #add trade to portfolio
            self.portfolio.sellTransaction(newOrder)
            #remove positions 
            self.position.removePosition(newOrder['symbol'],newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares'])            

        newOrder.update()
        self.order.order.flush()
        return price

    def execute(self):
        '''
        @summary: This function iterates through the orders and attempts to execute all the ones that are still valid and unfilled
        '''
        count = 0
        for order in self.order.getOrders():
            if order['timestamp'] == self.currTimestamp:
                if order['fill/timestamp'] == 0:
                    #Have unfilled, valid orders
                    if order['task'].upper() == "BUY":
                        #is a buy
                        if self.portfolio.hasStock(order['symbol'],1):
                            print order['symbol']
                            result = self.buyStock(order)
                            if noisy:
                                if result is not None:
                                    print "Succeeded in buying %d shares of %s for %.2f. Placed at: %s." % (order['shares'], order['symbol'], result, order['timestamp']),
                                    print "Current timestamp: %s, order #%d" % (self.currTimestamp, count)
                                else:
                                    print "THIS IS MOST LIKELY WRONG"
                        else:
                            result = self.buyStock(order)
                            if noisy:
                                if result:
                                    print "Succeeded in buying %d shares of %s for %.2f. Placed at: %s." % (order['shares'], order['symbol'], result, order['timestamp']),
                                    print "Current timestamp: %s, order #%d" % (self.currTimestamp, count)
                                else:
                                    print "Did not succeed in buying %d shares of %s. Placed at: %s." % (order['shares'], order['symbol'], order['timestamp']),
                                    print "Current timestamp: %s, order #%d" % (self.currTimestamp, count)
                    elif order['task'].upper() == "SELL":
                        # is a sell
                        result = self.sellStock(order)
                        if noisy:
                            if result:
                                print "Succeeded in selling %d shares of %s for %.2f." % (order['shares'], order['symbol'], result),
                                print "Current timestamp: %s" % (self.currTimestamp)
                            else:
                                print "Did not succeed in selling %d shares of %s; not enough owned." % (order['shares'], order['symbol']),
                                print "Current timestamp: %s" % (self.currTimestamp)
                    else:
                        if noisy:
                            print "'%s' is not a valid task.  Current timestamp: %s" % (order['task'].upper(), self.currTimestamp)
        count += 1

    def addOrders(self,trades):
        '''
        @summary: takes in trades (return value of strategy), parses it, and adds it in the correct format to the order data storage
        '''
        for trade in trades:
            self.order.addOrder(self.getExecutionTimestamp(trade),trade[3],trade[4],trade[5])

    def getExecutionTimestamp(self, trade):
        '''
        @summary: returns the timestamp of the current execution timestamp
        '''
        return dt.datetime(trade[0], trade[1], trade[2], 16)

    def run(self):
        '''
        @summary: Run the simulation
        '''
        timeofday = dt.timedelta(hours=16)
        timestamps = du.getNYSEdays(self.startTime,self.endTime,timeofday)
        portfolioValList = list()

        if timersActive:
            print "Simulation timer started at "+ str(self.currTimestamp)
            totalTime = time.time()
            cycTime = time.clock()

        beforeAddOrders = time.clock()
        trades = dollarStrategy(self.strategyData)
        sortedTrades = sorted(trades, key=itemgetter(0, 1, 2))
        self.addOrders(sortedTrades)
        afterAddOrders = time.clock()

        i = 1
        for timestamp in timestamps:
            self.currTimestamp = timestamp
            beforeExec=time.clock()
            self.execute()
            afterExec= time.clock()

            if noisy or timersActive:
                print '' #newline                
            if mtm:
                portValue= float (0.0)
                print "| %s %.2f |"%(self.currTimestamp,portValue) + "  Value from portfolio class: " +  str (self.portfolio.calcPortfolioValue(self.currTimestamp, self.strategyData))
            if timersActive and not noisy:
                print "Strategy at %s took %.4f secs"%(self.currTimestamp,(time.clock()-cycTime))
                i+=1
                cycTime = time.clock()
            if noisy and not timersActive:
                portValue = (self.portfolio.calcPortfolioValue(self.currTimestamp, self.strategyData)) 
                portfolioValList.append(portValue)
                
                print "Strategy at %s completed successfully." % self.currTimestamp
                print "Current cash: " + str(self.portfolio.currCash)
                print "Current stocks: %s."%self.portfolio.currStocks
                print "Current portfolio value: "+ str(portValue)+"\n\n"
            if noisy and timersActive:
                portValue =  float (self.portfolio.calcPortfolioValue(self.currTimestamp, self.strategyData))
                portfolioValList.append(portValue)
                
                print "Strategy at %s took %.4f secs"%(self.currTimestamp,(time.clock()-cycTime))
                print "Exec function took: " + str(afterExec - beforeExec)
                print "Time for addorders: " + str(afterAddOrders - beforeAddOrders)
                
                print "Strategy at %s completed successfully." % self.currTimestamp
                print "Current cash: " + str(self.portfolio.currCash)
                print "Current stocks: %s."%self.portfolio.currStocks
                print "Current portfolio value: "+ str(portValue)+"\n\n"
                i+=1
                cycTime = time.clock() 

        if noisy:
            print "Simulation complete."
        if timersActive:
            print "Simulation complete in %i seconds."%(time.time() - totalTime)

        self.portfolio.close()
        self.position.close()
        self.order.close()

        #plotting the portfolio value
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.plot (portfolioValList)
        ax.set_title('Portfolio value')
        ax.grid(True)
        ax.set_xlabel('time')
        ax.set_ylabel('$')
        canvas.print_figure('portfolio')
        #def run ends

cash = 0
noisy = True; timersActive = True; mtm = True

def main():
    global cash, noisy, timersActive, mtm

    parser = OptionParser()
    args = parser.parse_args()[1]

    if len(args) != 1:
	print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING."
        exit()

    try:
        cash = float(args[0])
    except ValueError:
        print "ARGUMENT FOR CASH IS NOT A FLOAT!"

    mySim = Simulator(cash)
    mySim.run()

if __name__ == "__main__":
    main()
