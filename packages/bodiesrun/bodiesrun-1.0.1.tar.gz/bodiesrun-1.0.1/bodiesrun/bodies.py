import numpy as np

from Body import Body

class Bodies:
    def __init__(self,lis:list,bn:int,tms=0.1):
        self.stars=[Body(lis[i][0],lis[i][1],lis[i][2]) for i in range(0,bn)]
        self.TIMESTEP = tms
    
    def run(self,t:int)->None:
        for _ in range(0,t/self.TIMESTEP):
            for body in self.stars:
                st = self.stars[:]
                st.remove(body)
                body.update(st,self.TIMESTEP)
        
