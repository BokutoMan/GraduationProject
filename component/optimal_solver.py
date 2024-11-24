import cvxpy as cp
import numpy as np
from comm import timer_decorator
import component.MathUtils as tool
from scipy.sparse import csr_matrix, isspmatrix
import scipy.sparse as sp

def compute_sample_properties(DFH):
    """
    根据 DFH 计算 D_of_sample、N_of_sample 和 Max_of_sample。

    :param DFH: 样本的频率直方图，可以是 numpy array 或 scipy.sparse 的稀疏矩阵。
    :return: (D_of_sample, N_of_sample, Max_of_sample) 元组。
    """
    if isspmatrix(DFH):
        # 如果是稀疏矩阵
        DFH = DFH.tocoo()  # 转为 COO 格式便于操作
        D_of_sample = int(DFH.data.sum())  # 样本总数
        N_of_sample = int((DFH.row * DFH.data).sum())  # 总权重
        Max_of_sample = DFH.shape[0]  # 样本的最大频率
    else:
        # 如果是普通数组或列表
        D_of_sample = int(sum(DFH))  # 样本总数
        N_of_sample = int(sum(i * count for i, count in enumerate(DFH)))  # 总权重
        Max_of_sample = len(DFH)  # 样本的最大频率

    return D_of_sample, N_of_sample, Max_of_sample

import numpy as np
from scipy.sparse import csr_matrix, isspmatrix

def pad_dfh(DFH, Max_of_S):
    """
    补零使 DFH 长度与 Max_of_S 匹配，并转换为列向量。

    :param DFH: 样本的频率直方图，可以是 numpy array 或 scipy.sparse 的稀疏矩阵。
    :param Max_of_S: 目标长度。
    :return: 补零后的列向量 (numpy array 或 scipy.sparse 的稀疏矩阵)。
    """
    if isspmatrix(DFH):
        # 如果是稀疏矩阵
        current_size = DFH.shape[0]
        if current_size < Max_of_S:
            # 补零行到 Max_of_S 长度
            padding = csr_matrix((Max_of_S - current_size, 1))
            DFH = csr_matrix(np.vstack([DFH.toarray(), padding.toarray()]))
        return DFH
    else:
        # 如果是普通数组
        padding_size = Max_of_S - len(DFH)
        DFH = np.pad(DFH, (0, padding_size), mode="constant", constant_values=0)
        return DFH.reshape(-1, 1)  # 转为列向量


@timer_decorator(msg="线性求解器,求解预期全数据集DFH(x)")
def solve_optimal_x(DFH, p, det=0.001, solver_options=None, verbose=True):
    """
    根据输入的DFH，计算最优的x。

    :param DFH: 样本的DFH (频率直方图)。
    :param D_of_sample: 样本unique总数。
    :param N_of_sample: 样本的总块数。
    :param Max_of_sample: 样本的最大频率。
    :param p: 采样率 (0 <= p <= 1)。
    :param det: 松弛因子，控制约束范围。
    :param solver_options: 求解器选项 (字典形式)。
    :return: 最优解 x 或 None（如果无解）。
    """

    # 从 DFH 计算样本的基本属性
    D_of_sample, N_of_sample, Max_of_sample = compute_sample_properties(DFH)
    # 数据准备
    D_of_S = int(D_of_sample / p)
    N_of_S = int(N_of_sample / p)
    Max_of_S = int(Max_of_sample / p)

    # 补零使 DFH 长度与 Max_of_S 匹配
    DFH = pad_dfh(DFH, Max_of_S)
    if sp.issparse(DFH):
        DFH_dense = DFH.toarray().flatten()  # 转换为 1D 稠密数组
    else:
        DFH_dense = DFH

    # 构建概率转移矩阵 Ap
    Ap = tool.build_probability_transition_matrix(Max_of_S, p)

    not_zero_cows = tool.get_nonzero_columns(Ap)

    # 定义优化变量
    x = cp.Variable((Max_of_S, 1), integer=False)

    # 定义目标函数
    weights = 1 / np.sqrt(DFH_dense + 1)  # 权重
    objective = cp.Minimize(cp.sum(cp.multiply(weights, cp.abs(DFH_dense - Ap @ x))))

    # 构建约束
    indices = np.arange(Max_of_S)
    get_sum_expr = cp.sum(cp.multiply(indices, x))
    constraints = [
        # cp.sum(x) - D_of_S <= D_of_S * 1 / 2,
        # cp.sum(x) - D_of_S >= D_of_S * -1 / 2,
        get_sum_expr - N_of_S <= N_of_S * det,
        # x >= 0,  # 非负约束
    ]
    # 添加其他条件：如果某列没有非零值，则 x[i] = 0
    for i in range(Max_of_S):
        if i not in not_zero_cows:
            constraints.append(x[i] == 0)  # x[i] 必须为 0
        else :
            constraints.append(x[i] >= 0)

    # 构建问题
    problem = cp.Problem(objective, constraints)

    # 设置求解器参数
    if solver_options is None:
        solver_options = {
            "limits/time": 100,  # 时间限制 100 秒
            "limits/gap": 0.1,  # GAP 限制 1%
            "display/verblevel": 5,  # 详细输出级别
            "max_iter": 1000,
        }

    # 求解问题
    print(f"Ap shape: {Ap.shape}")
    print(f"DFH_dense shape: {DFH_dense.shape}")
    print(f"Initial guess for x: {x.value}")

    # problem.solve(solver='ECOS', verbose=verbose)
    problem.solve(verbose=verbose)

    print(f"Ap shape: {Ap.shape}")
    print(f"DFH_dense shape: {DFH_dense.shape}")
    print(f"Initial guess for x: {x.value}")

    # 输出最优解
    if problem.status in ["optimal", "OPTIMAL"]:
        print("最优解找到：")
        print(f"和为: {x.value.sum()}")
        print(f"y': {(Ap @ x.value).shape}")
        return x.value
    else:
        print(f"问题未找到最优解，状态：{problem.status}")
        return None
    


if __name__=="__main__":
    # 示例使用
    @timer_decorator(msg="主函数")
    def main():
        # 示例参数
        D_of_sample = 900
        N_of_sample = 1000
        Max_of_sample = 100
        p = 0.5

        # 生成示例 DFH
        DFH = tool.generate_uniform_dfh(D_of_sample, Max_of_sample)

        # 计算最优解
        x_optimal = solve_optimal_x(
            DFH, p, det=0.001, verbose=True
        )

        # 输出结果
        if x_optimal is not None:
            N_of_sample = int(sum(i * count for i, count in enumerate(DFH)))
            N_of_S = int(N_of_sample / p)
            result = sum(x_optimal)/ N_of_S
            print("数据集的缩减效果", result)
            print("样本的缩减效果", D_of_sample/N_of_sample)

    main()
