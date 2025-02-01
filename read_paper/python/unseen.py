import numpy as np
from scipy.stats import poisson
from scipy.optimize import linprog

def unseen(f):
    # 输入：指纹 f，其中 f[i] 表示在样本中出现次数为 i 的元素数量。
    # 输出：真实分布的“直方图”近似值，histx[i] 表示具有概率 x[i] 的领域元素的数量。
    
    f = np.array(f).flatten()  # 将 f 转为一维数组
    k = np.dot(f, np.arange(1, len(f) + 1))  # 样本总大小

    # 算法参数
    grid_factor = 1.1  # 概率网格的几何比例
    alpha = 0.001  # 返回的解与“最佳”解之间允许的最大误差
    x_lp_min = 1 / (k * max(10, k))  # 最小允许的概率
    min_i = np.min(np.where(f > 0))  # 查找 f 中大于 0 的最小索引
    if min_i > 1:
        x_lp_min = min_i / k  # 如果 f 中有大于 0 的元素，更新最小允许的概率

    max_lp_iters = 1000  # 最大迭代次数


    # 算法部分

    # 将指纹分为密集部分和稀疏部分
    x = []
    histx = []
    dense_pl = np.zeros_like(f)

    for i in range(len(f)):
        if f[i] > 0:
            wind = [max(0, i - int(np.ceil(np.sqrt(i)))), min(i + int(np.ceil(np.sqrt(i))), len(f))]
            if np.sum(f[wind[0]:wind[1]]) < np.sqrt(i): # 2 * np.sqrt(i)
                # 小于 则该值为稀疏值
                x.append(i / k)
                histx.append(f[i])
                dense_pl[i] = 0
            else:
                # 否则为密集值，通过线性规划求解
                dense_pl[i] = f[i]

    # 如果没有 密集 部分，返回经验直方图
    try:
        max_pl_index = np.max(np.where(dense_pl > 0))
    except ValueError:
        # 全部元素都在稀疏区域，无密集区域
        print("全部元素都在稀疏区域，无密集区域")
        # 删除第一个元素，原因未知
        return np.array(x[1:]), np.array(histx[1:])

    # 设置第一个 LP
    dense_pl_sum = 1 - np.dot(x, histx)  # LP 区域中的概率质量
    # x 扩展 len(f)**0.5 个元素
    dense_pl = np.concatenate([dense_pl[:max_pl_index], np.zeros(int(np.ceil(np.sqrt(max_pl_index))))])  # 扩展 f_lp
    # y = Ax, x 的长度
    len_pl = len(dense_pl)

    # 最大允许的概率值
    max_pl = max_pl_index / k
    # 概率网格：一个数列，从 x_lp_min 开始，按照 grid_factor 等比增长直到 x_lp_max
    x_pl = x_lp_min * grid_factor ** np.arange(int(np.ceil(np.log(max_pl / x_lp_min) / np.log(grid_factor))) + 1)
    # A 的长度
    len_x = len(x_pl)

    # 约束的权重，频率越高，权重越低
    objf = np.zeros(len_x + 2 * len_pl)
    objf[len_x::2] = 1 / np.sqrt(dense_pl + 1)  # 根据频次计算目标函数
    objf[len_x + 1::2] = 1 / np.sqrt(dense_pl + 1)  # 权重为 1/sqrt(f(i)+1)

    A = np.zeros((2 * len_pl, len_x + 2 * len_pl))
    b = np.zeros(2 * len_pl)

    for i in range(len_pl):
        A[2 * i, :len_x] = poisson.pmf(i, k * x_pl)  # 计算泊松分布
        A[2 * i + 1, :len_x] = -A[2 * i, :len_x]
        A[2 * i, len_x + 2 * i] = -1
        A[2 * i + 1, len_x + 2 * i + 1] = -1
        b[2 * i] = dense_pl[i]
        b[2 * i + 1] = -dense_pl[i]

    Aeq = np.zeros(len_x + 2 * len_pl)
    Aeq[:len_x] = x_pl
    beq = dense_pl_sum

    options = {'maxiter': max_lp_iters, 'disp': True}
    for i in range(len_x):
        A[:, i] /= x_pl[i]  # 缩放矩阵
        Aeq[i] /= x_pl[i]

    Aeq = np.reshape(Aeq, (1, len(Aeq)))
    beq = np.reshape(beq, (1, len(np.array([beq]))))
    # 使用 linprog 求解线性规划
    """res : OptimizeResult
    A scipy.optimize.OptimizeResult consisting of the fields below. Note that the return types of the fields may depend on whether the optimization was successful, therefore it is recommended to check OptimizeResult.status before relying on the other fields:

    x : 1-D array
        The values of the decision variables that minimizes the objective function while satisfying the constraints.
    fun : float
        The optimal value of the objective function c @ x.
    slack : 1-D array
        The (nominally positive) values of the slack variables, b_ub - A_ub @ x.
    con : 1-D array
        The (nominally zero) residuals of the equality constraints, b_eq - A_eq @ x.
    success : bool
        True when the algorithm succeeds in finding an optimal solution.
    status : int
        An integer representing the exit status of the algorithm.

        0 : Optimization terminated successfully.

        1 : Iteration limit reached.

        2 : Problem appears to be infeasible.

        3 : Problem appears to be unbounded.

        4 : Numerical difficulties encountered.

    nit : int
        The total number of iterations performed in all phases.
    message : str
        A string descriptor of the exit status of the algorithm."""
    re = linprog(objf, A_eq=Aeq, b_eq=beq, A_ub=A, b_ub=b, bounds=[(0, np.inf)] * (len_x + 2 * len_pl), options=options)
    fval, exitflag = re.fun, re.success
    print(fval, exitflag)
    if exitflag == 0:
        print("最大迭代次数已达到--尝试增加 maxLPiters")

    if exitflag < 0:
        print("LP1 解未找到，仍然尝试解 LP2...")

    # 求解第二个 LP，最小化支持集的大小
    objf2 = np.zeros_like(objf)
    objf2[:len_x] = 1  # 保证目标函数至多相差 alpha
    A2 = np.vstack([A, objf])
    b2 = np.concatenate((b, np.array([fval + alpha])), axis=0)

    for i in range(len_x):
        objf2[i] /= x_pl[i]  # 对目标函数进行缩放

    re2 = linprog(objf2, A_eq=Aeq, b_eq=beq, A_ub=A2, b_ub=b2, bounds=[(0, None)] * (len_x + 2 * len_pl), options=options)
    sol2, exitflag2 = re2.x, re2.success
    if exitflag2 != 1:
        print("LP2 解未找到")

    # 将 LP 解与经验部分的直方图合并
    print("sol2:", sol2)
    sol2[:len_x] = sol2[:len_x] / x_pl
    x = np.concatenate([x, x_pl])
    histx = np.concatenate([histx, sol2])

    # 对结果按 x 排序
    sort_idx = np.argsort(x)
    x = np.array(x)[sort_idx]
    histx = np.array(histx)[sort_idx]

    # 删除 0 频次的部分
    non_zero_idx = histx > 0
    x = x[non_zero_idx]
    histx = histx[non_zero_idx]

    return x, histx
