import numpy as np
import math

class Body:
    def __init__(self, weight, pos0, v0):
        self.m = weight
        self.pos = pos0
        self.v = v0

    def update(self, others, delta_t):
        # ���µ�ǰ�����λ��
        # others�洢ǰһʱ������body��pos��m��list����
        ft = np.array([0, 0, 0])
        for bodyi in others:
            # ���������ĵ�λ����
            ft_dir = (bodyi.pos - self.pos) / np.linalg.norm(bodyi.pos - self.pos)
            # ������������Ϊ1
            ft = ft + (bodyi.m * self.m / sum(np.square(bodyi.pos - self.pos))) * ft_dir
        at = ft / self.m
        # λ�ø��£�delta_r = v*delta_t + 0.5*a*(delta_t**2)
        self.pos = self.pos + self.v * delta_t + 0.5 * at * (delta_t ** 2)
        # �ٶȸ��£�delta_v = a*delta_t
        self.v = self.v + at * delta_t
        
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
                
class BodiesSR:
    def __init__(self,bn:int,lis:list,tms=0.1):
        li=[]
        for v in lis:
            li.append((v[0]*math.sqrt(3),
                       np.array(v[1]),
                       np.array(v[2])))
        self.bds=Bodies(bn,li,tms)