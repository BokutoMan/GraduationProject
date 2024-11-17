import cvxpy as cp
import numpy as np

# 示例数据
y = np.random.randint(0, 10, size=(10, 1))  # (10, 1) 向量
A = np.random.binomial(10, 0.5, (10, 10))  # (10, 100) 矩阵
print("y: ", y)
print("A:" , A)
# 定义变量
x = cp.Variable((10, 1), integer=True)

# 定义目标函数为 L1 范数
objective = cp.Minimize(cp.norm(y - A @ x, 1))

# 添加约束条件
constraints = [
    cp.sum(x) == 10 * cp.sum(y),  # 等式约束
    x >= 0,  # 非负约束
]

# 构建问题
problem = cp.Problem(objective, constraints)

# 求解问题
problem.solve(solver=cp.GLPK_MI)  # 使用 GLPK 求解器

# 输出结果
if problem.status == cp.OPTIMAL:
    print("最优解：")
    print(x.value)
else:
    print("问题未找到最优解。")
