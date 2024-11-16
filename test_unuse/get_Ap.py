import numpy as np
from scipy.special import comb

def build_probability_transition_matrix(max_frequency, p):
    """
    构建概率转移矩阵 A_p。

    :param max_frequency: 原始DFH的维度（文档频率的最大值加1）。
    :param p: 采样比例。
    :return: 概率转移矩阵 A_p。
    """
    # 初始化矩阵A_p，所有元素为0
    A_p = np.zeros((max_frequency, max_frequency))
    
    # 填充矩阵A_p
    for j in range(max_frequency):  # 对于每个原始频率j
        for i in range(max_frequency):  # 对于每个可能的新频率i
            # 计算原始频率j变为新频率i的概率
            prob = comb(j, i) * (p ** i) * ((1 - p) ** (j - i))
            A_p[i, j] = prob
    
    return A_p

# 定义一个函数来计算向量y'
def compute_yPrime(Ap, xPrime):
    yPrime = np.dot(Ap, xPrime)
    return yPrime


import numpy as np

def generate_uniform_dfh(total_docs, max_frequency):
    """
    生成一个均匀分布的文档频率直方图（DFH）。

    :param total_docs: 文档的总数。
    :param max_frequency: 文档可能出现的最大频率。
    :return: 文档频率直方图（DFH）。
    """
    # 计算每个频率下大约有多少文档
    num_docs_per_frequency = total_docs // (max_frequency + 1)
    
    # 剩余的文档需要平均分配到各个频率
    remainder = total_docs % (max_frequency + 1)
    
    # 初始化DFH，所有条目设置为num_docs_per_frequency
    dfh = np.full(max_frequency + 1, num_docs_per_frequency, dtype=int)
    
    # 将剩余的文档平均分配到各个频率
    for i in range(remainder):
        dfh[i] += 1
    
    return dfh

# 示例：生成一个总数为100，最高频率为5的DFH
total_docs = 100
max_frequency = 50
dfh = generate_uniform_dfh(total_docs, max_frequency)
print(dfh)


# 示例：构建一个维度为4（文档频率为0, 1, 2, 3）且采样比例为10%的概率转移矩阵
# 测试我们的函数
# if __name__ == "__main__":
# 参数设置
p = 0.5  # 采样比例
m = 50  # 文档频率的最大值

# 计算 Ap 矩阵
Ap = build_probability_transition_matrix(m+1, p)

# 计算 yPrime 向量
yPrime = compute_yPrime(Ap, dfh)


import numpy as np

def round_to_even(float_array):
    """
    将浮点数数组舍入到最近的偶数，保持总和不变。

    :param float_array: 输入的浮点数数组。
    :return: 转换后的整数数组。
    """
    # 计算原始数组的总和
    original_sum = np.sum(float_array)
    
    # 四舍五入到最近的整数
    rounded_array = np.round(float_array).astype(int)
    
    # 计算舍入后的总和
    rounded_sum = np.sum(rounded_array)
    
    # 计算舍入误差
    error = original_sum - rounded_sum
    
    # 如果误差不为0，调整最后一个元素以保持总和不变
    if error != 0:
        # 找到最后一个非零元素
        last_non_zero_index = np.where(rounded_array != 0)[0][-1]
        # 调整最后一个非零元素
        rounded_array[last_non_zero_index] += int(error)
    
    return rounded_array

# 示例：转换给定的浮点数数组为整数数组，保持总和不变

int_array = round_to_even(yPrime)
print(int_array)
# print("Original sum:", np.sum(yPrime))
print("New sum:", np.sum(int_array))


# 打印结果
# print("Ap matrix:\n", Ap)
print("\nxPrime vector:\n", dfh)
# print("\nyPrime vector:\n", yPrime)

print(sum(yPrime))
print(sum(dfh))

print(len(yPrime))


