def dollarStrategy(stockInfo):

    close = stockInfo.priceArray
    output = []

    for symbol in stockInfo.symbolIndex:
        for today in range(2,len(close[symbol])):
            yesterday = today - 1
            if close[symbol][yesterday] >=7.0 and close[symbol][today] < 7.0 :
                output.append((close.index[today].year, close.index[today].month, close.index[today].day, symbol, 'BUY', 100))

                sellDay = today + 5
                if (sellDay > len(close[symbol])):
                    sellDay = len(close[symbol])

                output.append((close.index[sellDay].year, close.index[sellDay].month, close.index[sellDay].day, symbol, 'SELL', 100))

    return output

