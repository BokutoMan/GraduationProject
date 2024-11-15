from scipy.optimize import linprog

# 目标函数系数（需要最小化的目标函数）
c = [-1, -2]  # 最小化 x + 2y

# 不等式约束 A_ub * x <= b_ub
A_ub = [[-1, 1], [1, 2]]  # -x + y <= 0 and x + 2y <= 2
b_ub = [0, 2]  # 不等式约束的右侧常数

# 等式约束 A_eq * x == b_eq
A_eq = [[1, -1]]  # x - y = 0
b_eq = [0]  # 等式约束的右侧常数

# 决策变量的上下界
# bounds = [(下界, 上界), ...] 对于每个决策变量
bounds = [(0, None), (0, None)]  # x 和 y 都不能小于 0

# 使用 linprog 函数求解
result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

if result.success:
    # 输出最优解和最优值
    print(f'最优解: x = {result.x}')
    print(f'最优值: {result.fun}')
else:
    print('没有找到解')
