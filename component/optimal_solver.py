import cvxpy as cp
import numpy as np
from comm import timer_decorator
import component.MathUtils as tool

def compute_sample_properties(DFH):
    """
    根据 DFH 计算 D_of_sample、N_of_sample 和 Max_of_sample。

    :param DFH: 样本的频率直方图 (numpy array)。
    :return: (D_of_sample, N_of_sample, Max_of_sample) 元组。
    """
    D_of_sample = int(sum(DFH))  # 样本总数
    N_of_sample = int(sum(i * count for i, count in enumerate(DFH)))  # 总权重
    Max_of_sample = len(DFH)  # 样本的最大频率
    return D_of_sample, N_of_sample, Max_of_sample

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
    padding_size = Max_of_S - len(DFH)
    DFH = np.pad(DFH, (0, padding_size), mode="constant", constant_values=0)
    DFH = DFH.reshape(-1, 1)  # 转为列向量

    # 构建概率转移矩阵 Ap
    Ap = tool.build_probability_transition_matrix(Max_of_S, p)

    # 定义优化变量
    x = cp.Variable((Max_of_S, 1), integer=False)

    # 定义目标函数
    weights = 1 / np.sqrt(DFH + 1)  # 防止除以 0
    objective = cp.Minimize(cp.sum(cp.multiply(weights, cp.abs(DFH - Ap @ x))))

    # 构建约束
    indices = np.arange(Max_of_S)
    get_sum_expr = cp.sum(cp.multiply(indices, x))
    constraints = [
        # cp.sum(x) - D_of_S <= D_of_S * 1 / 2,
        # cp.sum(x) - D_of_S >= D_of_S * -1 / 2,
        get_sum_expr - N_of_S <= N_of_S * det,
        x >= 0,  # 非负约束
    ]

    # 构建问题
    problem = cp.Problem(objective, constraints)

    # 设置求解器参数
    if solver_options is None:
        solver_options = {
            "limits/time": 100,  # 时间限制 100 秒
            "limits/gap": 1,  # GAP 限制 1%
            "display/verblevel": 5,  # 详细输出级别
            "max_iter": 1000,
        }

    # 求解问题
    problem.solve(verbose=verbose)

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
        p = 0.1

        # 生成示例 DFH
        DFH = tool.generate_uniform_dfh(D_of_sample, Max_of_sample)

        # 计算最优解
        x_optimal = solve_optimal_x(
            DFH, p, det=0.001, verbose=False
        )

        # 输出结果
        if x_optimal is not None:
            N_of_sample = int(sum(i * count for i, count in enumerate(DFH)))
            N_of_S = int(N_of_sample / p)
            result = sum(x_optimal)/ N_of_S
            print("数据集的缩减效果", result)
            print("样本的缩减效果", D_of_sample/N_of_sample)

    main()
