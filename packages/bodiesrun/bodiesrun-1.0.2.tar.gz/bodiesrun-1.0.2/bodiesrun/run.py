import math
import numpy as np
from bodies import Bodies

class BodiesSR:
    def __init__(self,bn:int,lis:list,tms=0.1):
        li=[]
        for v in lis:
            li.append((v[0]*math.sqrt(3),
                       np.array(v[1]),
                       np.array(v[2])))
        self.bds=Bodies(bn,li,tms)
        
