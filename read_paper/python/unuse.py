import numpy as np
from scipy.stats import poisson

len_pl = 2
len_x = 2
x_lp_min = 0.1
max_pl = 0.1
grid_factor = 1.1
k = 300
x_pl = x_lp_min * grid_factor ** np.arange(int(np.ceil(np.log(max_pl / x_lp_min) / np.log(grid_factor))) + 1)
# A 的长度
len_x = len(x_pl)
dense_pl = np.array([1, 2, 3 , 1, 0, 0, 0])

A = np.zeros((2 * len_pl, len_x + 2 * len_pl))
b = np.zeros(2 * len_pl)

for i in range(len_pl):
    A[2 * i, :len_x] = poisson.pmf(i, k * x_pl)  # 计算泊松分布
    A[2 * i + 1, :len_x] = -A[2 * i, :len_x]
    A[2 * i, len_x + 2 * i] = -1
    A[2 * i + 1, len_x + 2 * i + 1] = -1
    b[2 * i] = dense_pl[i]
    b[2 * i + 1] = -dense_pl[i]

print(A)