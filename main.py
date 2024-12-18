from utils import Reader, SimpleLogger
from component.HashCount import HashCount
import component.MathUtils as tool
from component import compute_dfh_use_counter, solve_optimal_x
from comm import timer_decorator
from component.optimal_solver import compute_sample_properties, pad_dfh

from scipy.sparse import csr_matrix
import scipy.sparse as sp

def dfh_to_sparse_vector(dfh, max_index=None):
    """
    将 DFH 转换为稀疏矩阵的一维列向量。

    :param dfh: 列表，格式为 [(索引, 值), ...]，如 [(2, 523998), (12, 1), (14, 1), (492, 1)]。
    :param max_index: 稀疏向量的最大索引（可选）。如果为 None，将根据 DFH 数据自动推断。
    :return: 稀疏矩阵形式的列向量（csr_matrix）。
    """
    # # 使用生成器表达式过滤第一个值大于10的元组
    # dfh = [(i, v) for i, v in dfh if v < 10]
    # 提取索引和值
    indices, values = zip(*dfh)

    # 自动推断最大索引（如果未提供）
    if max_index is None:
        max_index = max(indices) + 1  # 最大索引加 1 作为大小

    # 创建稀疏矩阵
    sparse_vector = csr_matrix((values, (indices, [0] * len(indices))), shape=(max_index, 1))
    return sparse_vector


@timer_decorator("main函数: 使用counter统计频率")
def main():
    datas = Reader.get_reader(new=True)  # 获取数据块迭代器
    dfh = compute_dfh_use_counter(datas, log_interval=100000)  # 计算 DFH
    print(dfh)  # 输出直方图
    p = 0.3

    # 转换为稀疏矩阵
    dfh = dfh_to_sparse_vector(dfh)
    # 打印结果
    print("稀疏矩阵（列向量）：")
    print(dfh)
    dfh_flatten = dfh.toarray().flatten()

    D_of_sample, N_of_sample, Max_of_sample = compute_sample_properties(dfh_flatten)
    print(D_of_sample, N_of_sample, Max_of_sample)

    DFH = dfh_flatten + 1.0e-30
    # 计算最优解
    x_optimal = solve_optimal_x(
        DFH, p, det=0.001, verbose=True
    )

    # 输出结果
    if x_optimal is not None:
        N_of_sample = int(sum(i * count for i, count in enumerate(DFH)))
        N_of_S = int(N_of_sample / p)
        result = sum(x_optimal)/ N_of_S
        print("x: ", x_optimal)
        print("数据集的缩减效果", result)
        print("样本的缩减效果", D_of_sample/N_of_sample)
        print("稀疏矩阵（列向量）：")
        print(dfh)

main()