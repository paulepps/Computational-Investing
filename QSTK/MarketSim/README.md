# Computational Investing #
## Market Simulator ##

A basic market simulator that accepts trading orders and keeps track of a portfolio's value.

Takes a command line like this:


    python marketsim.py 1000000 orders.csv

The number represents starting cash and orders.csv is a file of orders organized like this:

- Year
- Month
- Day
- Symbol
- BUY or SELL
- Number of Shares

For example:

    2008, 12, 3, AAPL, BUY, 130
    2008, 12, 8, AAPL, SELL, 130
    2008, 12, 5, IBM, BUY, 50

The simulator calculates and outputs the total value of the portfolio for each day using **adjusted closing prices**. The output should look something like this:

    2008, 12, 3, 1000000
    2008, 12, 4, 1000010
    2008, 12, 5, 1000250
    ...