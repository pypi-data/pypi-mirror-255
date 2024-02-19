import numpy as np

class Body:
    def __init__(self, weight, pos0, v0):
        self.m = weight
        self.pos = pos0
        self.v = v0

    def update(self, others, delta_t):
        # 更新当前天体的位置
        # others存储前一时刻所有body的pos和m，list类型
        ft = np.array([0, 0, 0])
        for bodyi in others:
            # 各个引力的单位向量
            ft_dir = (bodyi.pos - self.pos) / np.linalg.norm(bodyi.pos - self.pos)
            # 设置引力常数为1
            ft = ft + (bodyi.m * self.m / sum(np.square(bodyi.pos - self.pos))) * ft_dir
        at = ft / self.m
        # 位置更新，delta_r = v*delta_t + 0.5*a*(delta_t**2)
        self.pos = self.pos + self.v * delta_t + 0.5 * at * (delta_t ** 2)
        # 速度更新，delta_v = a*delta_t
        self.v = self.v + at * delta_t
