from read_paper.python.unseen import unseen
from read_paper.python.makeFinger import makeFinger

import numpy as np

import numpy as np

# 假设 makeFinger 和 unseen 函数已经被定义在当前环境中

# 生成一个随机样本数据（例如，从均匀分布中抽取样本）
# n = 200000  # 每个样本的支持大小
# k = 100000000  # 样本大小
# samp = np.random.randint(1, n+1, size=k)  # 从 1 到 n 的均匀分布中生成样本

# # 计算样本的指纹
# fingerprint = makeFinger(samp)
from data import  data
from comm import sparse_to_dense
fingerprint = sparse_to_dense(data)

print("样本指纹：")
print(fingerprint)
print("样本指纹的形状：")
print(fingerprint.shape)
print("最大值：")
print(np.max(fingerprint))

# 使用 unseen 函数估计真实分布的直方图
x, histx = unseen(fingerprint)

# 打印结果
print("估计的概率分布 (x):")
print(x)
print("估计的频率分布 (histx):")
print(histx)
print("sum(histx)：", np.sum(histx))
print("sum(fingerprint)：", np.sum(fingerprint))

from component.MathUtils import get_sum_num
print("sum(histx * num)：", get_sum_num(histx))
print("sum(fingerprint * num)：", get_sum_num(fingerprint))
print("sum_big/sum_simp: ", get_sum_num(histx)/get_sum_num(fingerprint))
print("样本压缩率：", np.sum(fingerprint)/get_sum_num(fingerprint))
print("估计总体压缩率：", np.sum(histx)/get_sum_num(histx))

# # 计算估计的熵
# estimated_entropy = -np.sum(histx * x * np.log(x))
# print("估计的熵：", estimated_entropy)

# # 输出真实分布的熵（对于均匀分布）
# true_entropy = np.log(n)  # 均匀分布的熵为 log(n)
# print("真实分布的熵：", true_entropy)

# 样本压缩率： [0.85334781]
# 估计总体压缩率： 0.8660424141027021
#  [0.73915761]