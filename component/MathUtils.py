import numpy as np
from scipy.special import comb
from comm import timer_decorator
from scipy.sparse import csr_matrix

@timer_decorator(msg="生成Ap")
def build_probability_transition_matrix(max_frequency, p):
    """
    构建稀疏概率转移矩阵 A_p (抽奖矩阵)

    :param max_frequency: 最大重复次数 (最大的抽奖池子)。
    :param p: 采样比例 (抽出比例为p的样品)。
    :return: 稀疏概率转移矩阵 A_p (csr_matrix 格式)。
    """
    rows, cols, data = [], [], []
    
    # 稀疏性规则定义
    # [(0, 100), (1, 50), (2, 25), (3, 12), (4, 7), (5, 3), (6, 1), (7, 1), (10, 1)]
    def sampling_step(value):
        return pow(2, value//100)

    # 填充稀疏矩阵
    for j in range(max_frequency):  # 遍历频率范围
        step = sampling_step(j)
        if j % step == 0:  # 根据稀疏性规则选择值
            for i in range(max_frequency):  # 计算抽中 i 块的概率
                prob = comb(j, i) * (p ** i) * ((1 - p) ** (j - i))
                if prob > 0:  # 仅存储非零概率值
                    rows.append(i)
                    cols.append(j)
                    data.append(prob)
    
    # 构建稀疏矩阵
    sparse_matrix = csr_matrix((data, (rows, cols)), shape=(max_frequency, max_frequency))
    return sparse_matrix
    
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
        # 调整第一个元素, 第一个是抽中0次的个数，是绝对多数，改变的影响应该更小
        rounded_array[0] += int(error)
    
    return rounded_array

@timer_decorator(msg="生成DFH")
def generate_uniform_dfh(D_of_sample, Max_of_sample):
        """
        生成一个随机分布的文档频率直方图（DFH）。

        :return: 文档频率直方图（DFH）。
        """
        dfh = []
        avg_num = D_of_sample // (Max_of_sample)
        import random
        for _ in range(Max_of_sample):
            dfh.append(random.randint(0,avg_num*2))
        # 处理多余的或者不足的
        dfh.sort(reverse=True)
        delta = D_of_sample - sum(dfh)
        if delta >= 0:
            dfh[0] += delta
        else:
            i = 0
            delta = -delta
            while delta != 0:
                t = dfh[i] - 1
                dfh[i] -= min(delta, t)
                delta -= min(delta, t)
                i += 1
        dfh.sort(reverse=True)   
        import numpy as np       
        return np.array(dfh)

def get_sum_num(l:list):
    sum = 0
    for i, num in enumerate(l):
        sum += i*num
    return sum