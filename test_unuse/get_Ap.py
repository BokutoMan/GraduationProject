from scipy.special import comb
from comm import timer_decorator
from utils import SimpleLogger
# 定义集合大小和试验次数

@timer_decorator
def get_Ap(N, n):
    """N = 10  集合中元素的总数
         n = 5   试验次数"""

    # 初始化矩阵 A_p，所有元素为0
    A_p = [[0 for j in range(n+1)] for i in range(n+1)]

    # 计算不重复采样的二项概率并填充矩阵
    for i in range(1, n+1):  # 从1开始，因为至少需要一次试验
        for j in range(i+1):  # 在 i 次试验中，成功的次数 j 最多为 i
            # 计算在不重复采样下，i次试验中得到j次成功的概率
            # 第一次成功的概率是 N 中特定元素的概率，之后每次成功的概率都会减少
            prob = (1/N)**j * ((N-1)/N)**(i-j) * comb(i, j)
            A_p[i][j] = prob
    return A_p

# # 打印矩阵 A_p
# for row in A_p:
#     print(row)
