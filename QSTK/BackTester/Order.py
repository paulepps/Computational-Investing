import tables as pt, numpy as np
from OrderModel import OrderModel

class Order:
    def __init__(self):
        self.orderFile = pt.openFile('OrderModel.h5', mode = "w")
        self.order = self.orderFile.createTable('/', 'order', OrderModel)
        self.orderArray = np.array([])

    def addOrder(self,timestamp,symbol,task,shares): 
        ''' 
        @param timestamp: the exact timestamp when the order was submitted
        @param symbol: the symbol abbreviation of the stock
        @param task: buy, sell, short, cover
        @param shares: the number of shares to trade
        
        @summary: adds a new unfulfilled order to the orders table
        @returns a reference to the row
        '''  
        return self.addOrderArray(timestamp,symbol,task,shares)
        
    def getOrders(self):
        '''
        @return: Returns all of the orders
        '''
        return self.orderArray

    def addOrderArray(self,timestamp,symbol,task,shares):  
        ''' 
        @param timestamp: the exact timestamp when the order was submitted
        @param symbol: the symbol abbreviation of the stock
        @param task: buy, sell
        @param shares: the number of shares to trade
        
        @summary: adds a new unfulfilled order to the orders table and returns the order
        '''  
        row = {}
        row['task'] = task
        row['shares'] = shares
        row['symbol'] = symbol
        row['timestamp'] = timestamp
        row['fill/timestamp'] = 0
        row['fill/quantity'] = 0
        row['fill/cashChange'] = 0
        self.orderArray = np.append(self.orderArray,row)
        return row

    def fillTable(self):
        '''
        @summary: converts all orders to HDF5 and outputs the file
        '''
        for arrRow in self.orderArray:
            row = self.order.row
            row['task'] = arrRow['task']
            row['shares'] = arrRow['shares']
            row['symbol'] = arrRow['symbol']
            row['timestamp'] = str(arrRow['timestamp'])
            row['fill/timestamp'] = str(arrRow['fill/timestamp'])
            row['fill/quantity'] = arrRow['fill/quantity']
            row['fill/cashChange'] = arrRow['fill/cashChange']
            row.append()
        self.order.flush() 
        
    def close(self):
        self.fillTable()
        self.orderFile.close()
