import numpy as np
from scipy.special import comb
from comm import timer_decorator

@timer_decorator(msg="生成Ap")
def build_probability_transition_matrix(max_frequency, p):
    """
    构建概率转移矩阵 A_p (抽奖矩阵)

    :param max_frequency: 最大重复次数(最大的抽奖池子)
    :param p: 采样比例(抽出比例为p的样品)
    :return: 概率转移矩阵 A_p (包含每个独立块抽中0-max块的概率)
    """
    # 初始化矩阵A_p，所有元素为0
    A_p = np.zeros((max_frequency, max_frequency))
    
    # 填充矩阵A_p
    for j in range(max_frequency):  # 对于频率为j的独立块
        for i in range(max_frequency):  # 抽中i块的概率
            # 计算从j块中抽到i块的概率
            prob = comb(j, i) * (p ** i) * ((1 - p) ** (j - i))
            A_p[i, j] = prob
    
    return A_p

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

if __name__=="__main__":

    generate_uniform_dfh(100, 20)
    # # 示例：生成一个D总数为100，最高频率为50的DFH
    # total_docs = 10000
    # max_frequency = 100
    # dfh = generate_uniform_dfh(total_docs, max_frequency)
    # print(dfh)

    # # 示例：构建一个维度为50且采样比例为50%的概率转移矩阵
    # # 参数设置
    # p = 0.5  # 采样比例
    # m = 100  # 文档频率的最大值

    # # 计算 Ap 矩阵
    # Ap = build_probability_transition_matrix(m+1, p)

    # # 计算 yPrime 向量
    # yPrime = compute_yPrime(Ap, dfh)

    # int_array = round_to_even(yPrime)
    # print("int_array(y')", int_array)
    # # print("Original sum:", np.sum(yPrime))
    # print("New sum:", np.sum(int_array))

    # print(sum(dfh))
    # print(sum(yPrime))

    # print(len(yPrime))
    # print("sum of sub", get_sum_num(yPrime))
    # print("sum of all:", get_sum_num(dfh))
    
    # print("shape of A:", Ap.shape)
    # print("shape of x:", dfh.shape)
    # print("shape of y' :", yPrime.shape)
    # print()
    # print("num of not zero in y':", np.count_nonzero(int_array))

    # yTrue = generate_uniform_dfh(total_docs, max_frequency)


