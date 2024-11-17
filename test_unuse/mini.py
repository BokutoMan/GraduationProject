import numpy as np
import test_unuse.get_Ap as tool
from comm import timer_decorator

"""
约定变量名如下:
    D_of_sample  样本的非重复块数
    N_of_sample  样本的块数
    Max_of_sample  样本中重复次数最多的块的数目

    D_of_S  整个数据集的非重复块数
    N_of_S  整个数据集的块数
    Max_of_S    整个数据集重复次数最多的块的数目

线性规划的目标函数参数:
    y : 样本的DFH     (Max_of_sample, 1)
    x : S的DFH        (Max_of_S, 1)
    p : 采样率        0 <= p <= 1
    Ap : 概率装移矩阵   (Max_of_S, Max_of_S)
    yPrime : 从S中以采样率p采样得到的样本的DFH    (Max_of_S, 1)

已知变量:
    sample的变量、N_of_S
    y, p 
计算过程:
    Max_of_S, D_of_S 需要估计,简单使用 Max_of_sample/p, D_of_sample/p 进行估计
    Ap = build_probability_transition_matrix(Max_of_S, p)
    将y补0到大小 (Max_of_S, 1)
    yPrime = Ap * x

    求使得 ||y - yPrime|| * weight  最小的 x

    满足条件: get_sum_num(y) = get_sum_num(x) * p = get_sum_num(yPrime)
            yPrime = Ap * x

"""
# D_of_sample = 9000
# N_of_sample = 10000
# Max_of_sample = 100

# p = 0.1

# D_of_S = int(D_of_sample/p)
# N_of_S = int(N_of_sample/p)
# Max_of_S = int(Max_of_sample/p)

@timer_decorator(msg="主程序消耗时间")
def main():
    D_of_sample = 9000
    N_of_sample = 10000
    Max_of_sample = 100

    p = 0.1

    D_of_S = int(D_of_sample/p)
    N_of_S = int(N_of_sample/p)
    Max_of_S = int(Max_of_sample/p)


    # y : 样本的DFH     (Max_of_sample, 1)
    y = tool.generate_uniform_dfh(D_of_sample, Max_of_sample)
    N_of_sample = tool.get_sum_num(y)
    N_of_S = int(N_of_sample/p)
    assert len(y) == Max_of_sample
    assert sum(y) == D_of_sample

    # x : S的DFH        (Max_of_S, 1)
    # p : 采样率        0 <= p <= 1
    # Ap : 概率装移矩阵   (Max_of_S, Max_of_S)
    # yPrime : 从S中以采样率p采样得到的样本的DFH    (Max_of_S, 1)

    Ap = tool.build_probability_transition_matrix(Max_of_S, p)
    print(Ap.shape)

    x = tool.generate_uniform_dfh(D_of_S, Max_of_S)
    yPrime = Ap.dot(x)

    # 给y 补零
    padding_size = Max_of_S - y.shape[0]
    y = np.pad(y, (0, padding_size), mode='constant', constant_values=0)

    assert y.shape == yPrime.shape

    # 计算 Δ_p(x', y)
    delta_p = np.sum(1 / np.sqrt(y + 1) * np.abs(y - yPrime))

    print(" Δ_p(x', y): ", delta_p)

main()