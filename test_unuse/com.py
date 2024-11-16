import numpy as np
from scipy.optimize import linprog

def estimate_unseen(F, n, x):
  """
  使用线性规划估计未知分布的指纹。

  Args:
    F: 实际指纹，一个长度为 m 的向量，表示每个元素出现次数。
    n: 样本大小。
    x: 线性规划变量的概率值。

  Returns:
    h': 最优分布形状，一个长度为 len(x) 的向量。
    obj: 目标函数的最小值。
  """

  # 计算 Poisson 概率
  poi_probs = np.array([np.poisson(n * xi, i) for i in range(len(F) + 1)])

  # 构建线性规划问题
  c = np.array([1/np.sqrt(1 + fi) * abs(fi - np.dot(x, poi_probs[:, i])) for fi in F])
  A = np.array([x])
  b = np.array([1])
  bounds = [(0, None)] * len(x)

  # 求解线性规划问题
  result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

  # 返回结果
  h_prime = result.x
  obj = result.fun
  return h_prime, obj

# 示例
F = np.array([300, 78, 13, 1, 0, 0])
n = 500
x = np.array([1/1000, 2/1000, 3/1000, ..., 1000/1000])

h_prime, obj = estimate_unseen(F, n, x)

print("最优分布形状：", h_prime)
print("目标函数最小值：", obj)
