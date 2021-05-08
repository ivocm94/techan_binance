from numpy import std
from functools import reduce
from datetime import datetime, timedelta
from tanalysis.Candle import Candle
from tanalysis.Position import Position
from tanalysis.butils import sumCandles
import numpy as np
from numpy import mean
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import plotly.express as px

class Chart:
    def __init__(self, candles, name=None):
        self.name = name
        self.candles = []
        for c in candles:
            self.candles.append(Candle([c[0], c[1], c[2], c[3], c[4], c[5]]))
        self.length = len(candles)
        #self.interval = datetime.fromtimestamp((self[0].t-self[1].t)/1000)
        self.positions = []
        self.patterns = []
        #self.avgPrice
        #self.avgVolume 
        #self.priceStd
        #self.supports
        #self.resistances
        self.bufferCandle = []
        self.wonpositions = 0
        self.lostpositions = 0
        
    def addCandles(self, c):
        if type(c) == Candle:
            self.candles.append(c)
        elif type(c) == list:
            for candle in c:
                self.candles.append(candle)
        else:
            raise TypeError
        return True
    
    def candleBuffer(self, partialCandle):
        if len(self.positions) > 0:
            self.monitorPrice(partialCandle[4])       # demo 
        if partialCandle[-1]:
            wholeCandle = reduce(sumCandles, [x[:-1] for x in self.bufferCandle])
            self.addCandles(Candle(wholeCandle))
            self.bufferCandle = []
            return self.candles[-1]
        else:
            self.bufferCandle.append(partialCandle)
            return self.bufferCandle

    def plot(self):
        #fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.2], vertical_spacing=0.01, shared_xaxes=True)
        fig.add_trace(go.Candlestick(x=[c.dt for c in self.candles], 
            open=[float(c.o) for c in self.candles], 
            high=[float(c.h) for c in self.candles], 
            low=[float(c.l) for c in self.candles], 
            close=[float(c.c) for c in self.candles], 
            hovertext=[[format(c.volume, '.2f'),format(c.chgp, ".1f")+"%"] for c in self.candles]), 
            row=1, col=1)
        fig.update_layout(
            title=self.name+"\t\t"+str(self[0].dt)+" to "+str(self[-1].dt), 
            hovermode='x', 
            xaxis_rangeslider_visible=False, 
            xaxis=dict(showspikes=True))
        # add volume subplot 
        fig.add_trace(go.Bar(x=[c.dt for c in self.candles], y=[c.volume for c in self.candles], hoverinfo="none", opacity=0.3), row=2, col=1)
        fig.layout.yaxis2.showgrid=False
        fig.show() 

    def checkDescent(self, can, percent):
        if type(can) == slice:
            if self[can].chgp <= -percent:
                return True
            else:
                return False
        else:
            if len(self.candles) > can and self[-can::1].chgp <= -percent: #
                return True
            else:
                return False



        #if len(self.candles) > can and self[-can:].chgp<=-percent:
        #    return True
        #else:
        #    return False

#    def getHomogeneity(self, candles):
#        pass

    def monitorPrice(self, price):
        # check price to close positions (only for observations, for actual orders use Binance Websockets)
        print ("Monitoring price.")
        profits = [x for x in self.positions if price >= x.takeprofit and not x.closed]
        losses = [x for x in self.positions if price <= x.stoploss and not x.closed]
        if profits:
            for x in profits:
                x.close(True)
                self.positions.remove(x)
                self.wonpositions = self.wonpositions+1
        if losses:
            for x in losses:
                x.close(False)
                self.positions.remove(x)
                self.lostpositions = self.lostpositions+1



#    def positiveHammer(self, candleRange):
#        if self.checkDescent(candleRange)
#        if self[-1].isHammer
#        if len(bufferCandle) > 15 and bullish


#        if (chart.checkDescent(4, 0.3) or chart.checkDescent(5, 0.3)) and chart.candles[-1].isHammer and chart[-5:-2].l >= chart[-2].l:
#            if len(chart.bufferCandle) >= 15:
#                if Candle(reduce(sumCandles, [x[:-1] for x in chart.bufferCandle])).bullish:
#                    print("PLACING POSITION FOR HAMMER PATTERN")
#                    chart.positions.append(Position(chart[-1].t + 60000,"BUY", "10USD", chart.bufferCandle[-1][4], getPricePlusPercentage(chart.bufferCandle[-1][4], 0.4), getPricePlusPercentage(chart.bufferCandle[-1][4], -0.1)))
#                    chart.patterns.append ( [ chart[-5].t, chart[-1].t + 120000 ] 

    def avgVol (self, d1, d2):
        #plus = lambda x,y: x+y
        range = self[d1:d2]
        #return reduce(plus, [k.volume for k in range])/len(range)
        return mean([k.volume for k in range])
    
    def priceStd(self,d1, d2):
        return np.std([k.c for k in self[d1:d2]])

    def volumeStd (self, d1, d2):
        return np.std([k.volume for k in self[d1:d2]])

    def getSDMult(self, avgcan, evcan, sd=1):
        avgVol = self.avgVol(avgcan[0], avgcan[1])
        std = self.volumeStd (avgcan[0], avgcan[1])
        # calculate sd multiplier
        sdm = sd
        iter = True
        while iter:
            for k in self[avgcan[0]:avgcan[1]]:
                if k.volume > avgVol + sd*std:
                    sdm = sdm+1
                    continue
            iter = False
        return sdm            

    def MA(self, d1, d2):
        range = self[d1:d2]
        sumClosePrices= 0
        for k in range:
            sumClosePrices = sumClosePrices + k.c
        return sumClosePrices/len(range)

    def checkPriceAnomalies(self, d, sd=5):
        d1 = d-timedelta(hours=14)
        MA = self.MA(d1, d)
        std = self.priceStd(d1, d)
        anomalies = []
        prenomalies = []
        for k in self[d1:d]:
            if k.c > MA * sd*std:
                prenomalies.append(k)
        for k in self[d:]:
            if k.c > MA * sd*std:
                anomalies.append(k)
        return prenomalies, anomalies

    def getAnomalies(self, avgcan, evcan, quality, sdm=4):
        if quality in ['volume', 'price', 'chgp']:
            pass

    def getChgpAnomalies(self, avgcan, evcan, sdm=4):
        pass

    def getAvgRange(self, d1, d2):
        ran = self[d1:d2]
        return mean([k.range for k in ran])

    def getRangeAnomalies(self, avgcan, evcan, sdm=4):
        avgRange = self.getAvgRange(avgcan[0], avgcan[1])
        std = np.std([k.range for k in self[avgcan[0]:avgcan[1]]])
        anomalies = []
        prenomalies = []
        for k in self[avgcan[0]:avgcan[1]]:
            if k.range >avgRange+sdm*std:
                prenomalies.append(k)
        
        for k in self[evcan[0]:evcan[1]]:
            if k.range >avgRange+sdm*std:
                anomalies.append(k)
        return prenomalies, anomalies, avgRange, std

    def getVolumeAnomalies(self, avgcan, evcan, sdm=None, perc=None):
        avgVol = self.avgVol(avgcan[0], avgcan[1])
        std = self.volumeStd (avgcan[0], avgcan[1])
        mult = (perc/100) * avgVol if perc else sdm * std
        anomalies = []
        prenomalies = []
        for k in self[avgcan[0]:avgcan[1]]:
            if k.volume >avgVol+mult:
                prenomalies.append(k)
        
        for k in self[evcan[0]:evcan[1]]:
            if k.volume > avgVol + mult:
                anomalies.append(k)

        return prenomalies, anomalies,  avgVol, std, [self[avgcan[0]:avgcan[1]:1].chgp, self[evcan[0]:evcan[1]:1].chgp]


    def __getitem__(self, key):
        plus = lambda x,y: x+y
        if type(key) == slice: # slice retrieval
            if key.step == None: # 0/None is no reduction
                if type(key.start) == datetime:  # [dt:?:0]
                    if type(key.stop) == datetime:  # [dt:dt:0]
                        return [k for k in self.candles if k.dt >= key.start and k.dt <= key.stop]
                    elif type(key.stop) == int:     # [dt:int:0]
                        return [k for k in self.candles if k.dt >= key.start and self.candles.index(k) <= key.stop]
                    else:                           # [dt:None:0]
                        return [k for k in self.candles if k.dt >= key.start]


                elif type (key.start) == int:    # [int:?:0]
                    if type(key.stop) == datetime:  # [int:dt:0]
                        return [k for k in self.candles if key.start <= self.candles.index(k) and k.dt <= key.stop]

                    elif type(key.stop) == int:     # [int:int:0] or [int:None:0]
                        return self.candles[key]

                else:                            # [None:?:0]
                    if type(key.stop) == datetime:   # [None:dt:0]
                        return [k for k in self.candles if k.dt <= key.stop]
                    else:     # [None:int:0]
                        return self.candles[key]


            elif key.step == 1: # 1 is whole reduction
                if type(key.start) == datetime and type(key.stop) == datetime:
                    return reduce(plus, self[key.start:key.stop])
                else:
                    return reduce(plus, self.candles[key.start:key.stop])

            else:               #check step and reduce accordingly
                pass

        else: # single element retrieval
            if type(key) == datetime:
                try:                    
                    return [k for k in self.candles if k.dt <= key and k.dt >= key][0]
                except:
                    return Candle.trivial()
            else:
                try:
                    return self.candles[key]
                except:
                    return Candle.trivial()

    def __len__(self):
        return len(self.candles)

    def __str__(self):
        return str(self.length)