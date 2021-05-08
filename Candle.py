from functools import reduce
from datetime import datetime
class Candle:
    def __init__(self, can):
        self.t = int(can[0])
        self.dt = datetime.fromtimestamp(self.t/1000)
        self.o, self.h, self.l, self.c, self.volume = [float(x) for x in can[1:]]
        self.bullish = 1 if self.c-self.o>0 else 0
        self.range = self.h - self.l
        self.body = self.c-self.o if self.bullish else self.o-self.c
        self.lTail = self.o-self.l if self.bullish else self.c-self.l
        self.uTail = self.h-self.c if self.bullish else self.h-self.o
        self.chgp = float(format(self.body/self.o * 100, '.3f')) if self.bullish else -float(format(self.body/self.o * 100, '.3f'))
    
    def isHammer(self):
        if self.uTail - 2*self.body >= 0 and self.lTail - 1.5*self.body <= 0: # inverted hammer
            return True

        elif self.lTail - 2*self.body >= 0 and self.uTail - 1.5*self.body <=0: # hammer
            return True
        #if self.lTail/self.body >= 2 and self.uTail/self.body < 1.5:
        #    return True
        #elif self.uTail/self.body >= 2 and self.lTail/self.body < 1.5:
        #    return True
        else:
            return False
        # could add hammer degrees, relative to longer/shorter tails and bodies.
    
    def isDoji(self):
        if self.lTail - 3*self.body >= 0 and self.uTail - 3*self.body >= 0:
            return True
        
        #if self.lTail == 0 or self.uTail == 0:
        #    return False
        #if self.lTail/self.body >= 3 and self.uTail/self.body >= 3:
        #    return True
        else:
            return False
    
    def __add__(self, c):
        return Candle([self.t, self.o, max(self.h, c.h), min(self.l, c.l), c.c, self.volume + c.volume])

    def __str__(self):
        return "Volume: "+format(self.volume, '.3f')+"\nBullish: "+str(+self.bullish)+"\nChange%: "+str(self.chgp)+"%\nt: "+str(self.t)+"\no: "+str(self.o)+"\nh: "+str(self.h)+"\nl: "+str(self.l)+"\nc: "+str(self.c)+"\nBody: "+format(self.body, '.3f')+"\nlTail: "+format(self.lTail, '.3f')+"\nuTail: "+format(self.uTail, '.3f')+"\nHammer: "+str(self.isHammer())+"\nDoji: "+str(self.isDoji())

    def trivial():
        return Candle([1, 1, 1, 1, 1, 1])