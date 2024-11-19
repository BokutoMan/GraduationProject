import cvxpy as cp
import numpy as np
from warps import timer_decorator
import component.com_Ap as tool

@timer_decorator(msg="主函数")
def main():
    # 数据准备
    D_of_sample = 900
    N_of_sample = 1000
    Max_of_sample = 100

    p = 0.1

    D_of_S = int(D_of_sample / p)
    N_of_S = int(N_of_sample / p)
    Max_of_S = int(Max_of_sample / p)

    det = 0.01

    # y : 样本的DFH     (Max_of_sample, 1)
    y = tool.generate_uniform_dfh(D_of_sample, Max_of_sample)
    N_of_sample = tool.get_sum_num(y)
    N_of_S = int(N_of_sample / p)
    assert len(y) == Max_of_sample
    assert sum(y) == D_of_sample
    # 给 y 补零
    padding_size = Max_of_S - y.shape[0]
    y = np.pad(y, (0, padding_size), mode="constant", constant_values=0)
    assert sum(y) == D_of_sample
    y = y.reshape(-1, 1)

    # x : S的DFH        (Max_of_S, 1)
    # p : 采样率        0 <= p <= 1
    # Ap : 概率装移矩阵   (Max_of_S, Max_of_S)
    # yPrime : 从S中以采样率p采样得到的样本的DFH    (Max_of_S, 1)

    Ap = tool.build_probability_transition_matrix(Max_of_S, p)
    print("Ap.shape: ", Ap.shape)

    # 定义变量
    x = cp.Variable((Max_of_S, 1), integer=False)

    # 定义目标函数
    weights = 1 / np.sqrt(y + 1)  # 预计算
    objective = cp.Minimize(cp.sum(cp.multiply(weights, cp.abs(y - Ap @ x))))

    # 添加约束条件
    indices = np.arange(Max_of_S)
    get_sum_expr = cp.sum(cp.multiply(indices, x))
    constraints = [
        cp.sum(x) - D_of_S <= D_of_S * 1/2,  # 等式约束
        cp.sum(x) - D_of_S >= D_of_S *  -1/2,
        get_sum_expr - N_of_S <= N_of_S * det,
        x >= 0,  # 非负约束
    ]

    # 构建问题
    problem = cp.Problem(objective, constraints)

    # 设置 SCIP 求解器的参数
    solver_options = {
        "limits/time": 100,  # 设置时间限制为100秒
        "limits/gap": 1,  # 设置gap限制为1%
        "display/verblevel": 5,  # 设置详细输出级别
        'max_iter': 1000
    }

    # 求解问题，使用 SCIP
    problem.args.append(solver_options)
    problem.solve(verbose=True)


    # 输出结果
    if problem.status in ["optimal", "OPTIMAL"]:
        print("最优解：")
        print("和为:", x.value.sum())
        print("y': ", (Ap@x.value).reshape(1, -1))
        print("x", x.value.reshape((1, -1)))
    else:
        print(f"问题未找到最优解，状态：{problem.status}")


main()
