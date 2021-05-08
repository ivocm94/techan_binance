from functools import reduce
import math

def sumCandles(c1, c2=None):
    if c2 is not None:
        return [c1[0], c1[1], max(c1[2], c2[2]), min(c1[3], c2[3]), c2[4], c2[5]]
    elif type(c1) == list:
        return reduce(sumCandles, c1)
    else:
        raise TypeError ("Parameters can be either list or 2 candles")

def formatDec(value, dec):
    if type(value) == float:
        return float(format(value, '.'+str(dec)+'f'))
    else:
        return format(float(value), '.'+str(dec)+'f')

def getPricePlusPercentage(price, percentage):
    return str((float(percentage)/100)*float(price)+float(price))

def decimalPlaces(x):
    if type(x) == list:
        return list(map(decimalPlaces, x))
    else:
        d = str(x).split('.')[1]
        if int(d) == 0:
                print("2")
                return 0
        while d[-1] == '0':
            d = d[:-1]
        return len(d)
