import numpy as np
import math
from scipy.optimize import linprog

def poisson(lambda_, k):
    """
    n: 试验次数
    p: 成功概率(我们想要计算的真实概率)
    `λ` : n*p

    参数:
    lambda_ (float): 事件发生的平均速率（λ）。
    k (int): 事件发生的次数。

    返回:
    float: 在给定的λ下, 事件发生k次的概率。
    """

    # 计算 e^(-λ)
    exp_lambda = math.exp(-lambda_)
    # 计算 λ^k
    lambda_k = lambda_ ** k
    # 计算 k!
    k_fact = math.factorial(k)
    # 计算 PMF
    pmf = (exp_lambda * lambda_k) / k_fact
    
    return pmf

  
if __name__=="__main__":
    # 示例
    F = np.array([300, 78, 13, 1, 0, 0])
    n = 500
    x = np.array([1/1000, 2/1000, 3/1000, ..., 1000/1000])

    # h_prime, obj = estimate_unseen(F, n, x)

    # print("最优分布形状：", h_prime)
    # print("目标函数最小值：", obj)

    print(len(x))

    # 示例使用
    lambda_ = 2.0  # 事件发生的平均速率
    k = 3         # 事件发生的次数

    probability = poisson(lambda_, k)
    print(f"P(X = {k}) = {probability}")
