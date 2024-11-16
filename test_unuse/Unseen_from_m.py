import numpy as np
from scipy.optimize import linprog
def unseen_estimator(F, n, k, c, alpha):
    """
    Python 实现“未观察到的估计器”（Unseen Estimator），来自论文 "Estimating the Unseen: Improved Estimators for Entropy and Other Properties"。
    参数：
    - F: 二维指纹矩阵，每行对应第一个分布的样本，每列对应第二个分布的样本。
    - n: 样本大小。
    - k: 两个分布支持集大小的上限。
    - c: 网格点的几何比率。
    - alpha: 第二个线性规划中的误差参数。
    返回：
    - h_est: 估计的直方图。
    """
    # 计算网格点范围
    x = c ** np.arange(0, int(np.log(n / c) / np.log(c)))
    # 计算第一个大于 1/k 的网格点索引
    j = np.where(x > 1 / k)[0][0]
    # 计算第一个线性规划的索引
    x1 = x[:j] / n
    y1 = x[:j] / k
    # 求解第一个线性规划
    A_eq = np.vstack((np.ones(j), np.ones(j))).T
    b_eq = np.ones(2)
    bounds = [(0, None)] * (j * 2)
    v1 = linprog(-F, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')[0]
    # 计算第二个线性规划的索引
    x2 = x[:j + 1] / n
    y2 = x[:j + 1] / k
    # 求解第二个线性规划
    A_eq = np.vstack((np.ones(j + 1), np.ones(j + 1))).T
    b_eq = np.ones(2)
    bounds = [(0, None)] * ((j + 1) * 2)
    v2 = linprog(-F, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')[0]
    # 计算第一个大于 alpha 的网格点索引
    j2 = np.where(x2 > alpha)[0][0]
    # 计算第一个大于 1/alpha 的网格点索引
    j3 = np.where(x2 > 1 / alpha)[0][0]
    # 初始化估计的直方图
    h_est = np.zeros((j + 1, j + 1))
    # 根据线性规划的解填充估计的直方图
    h_est[:j, :j] = v1[:j, :j] * (1 - x1) * (1 - y1)
    h_est[j2:, j2:] = v2[j2:, j2:] * (1 - x2[j2:]) * (1 - y2[j2:])
    h_est[j2:, :j] = F[j2:, :j] / n / k
    h_est[:j, j2:] = F[:j, j2:] / n / k
    return h_est