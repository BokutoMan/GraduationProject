import numpy as np
from scipy.optimize import minimize
from get_Ap import build_probability_transition_matrix
import yaml

max = 7
p = 0.9
data = yaml.safe_load(open("test_unuse/data.yaml", 'r'))['y2']
print("data", data)
y = np.array(data)    # 用实际的y向量替换...
# y = np.random.randint(low=0, high=5, size=(5, ))
print("y: ", y)
# 变量的维度
n = len(y) * int(1/p)
# 使用pad函数在末尾补零
y = np.pad(y, (0, n - y.size), 'constant', constant_values=(0, 0))
# A_p 和 y 是已知的，并且已经定义为numpy数组
A_p = build_probability_transition_matrix(n, p)
print("shape Ap:", A_p.size)
N = sum(y) * int(1/p)
print("N:", N)
import numpy as np
from scipy.optimize import minimize

# 定义目标函数 Δ_p(x', y)
def delta_p(x_prime, y, A_p):
    return np.sum(1 / np.sqrt(y + 1) * np.abs(y - np.dot(A_p, x_prime)))

# 初始化数据
# 假设 A_p 是一个已知的矩阵，y 是已知的向量，N 是目标的总和



# 初始值
x0 = np.ones(n) / n

# 约束条件
constraints = [
    {"type": "eq", "fun": lambda x: np.sum(x * np.arange(1, 1+len(x))) - N},  # \\sum_i x'_i * i = N
    {"type": "ineq", "fun": lambda x: x}  # x'_i >= 0
]

# 优化
result = minimize(
    delta_p,  # 目标函数
    x0,       # 初始值
    args=(y, A_p),  # 目标函数的参数
    constraints=constraints,  # 约束条件
    bounds=[(0, None)] * n  # 保证所有 x'_i >= 0
)

# 输出结果
if result.success:
    print("优化成功！")
    print("最优解 x':", result.x)
    print("目标函数最小值:", result.fun)
    print("sum of x:",  sum(result.x))
    print("sum(x)/sum(y)",  sum(result.x)/ sum(y))
else:
    print("优化失败：", result.message)

