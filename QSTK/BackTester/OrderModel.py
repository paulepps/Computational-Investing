import tables as pt #@UnresolvedImport
import time

class FillModel(pt.IsDescription):
    timestamp = pt.StringCol(30)
    quantity = pt.Int32Col()
    cashChange = pt.Float32Col()
    
class OrderModel(pt.IsDescription):
    task = pt.StringCol(5)
    shares = pt.Int32Col()
    symbol = pt.StringCol(30)
    timestamp = pt.StringCol(30)
    fill = FillModel()
