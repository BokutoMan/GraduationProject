import numpy as np
from scipy.optimize import linprog

class Unseen:
    def __init__(self, dfh, p, tolerance=1e-5, epsilon=0.01, alpha=0.5, maxiter=1000):
        self.dfh = dfh
        self.p = p
        self.tolerance = tolerance
        self.epsilon = epsilon
        self.alpha = alpha
        self.maxiter = maxiter
        self.N = sum([i*j for i,j in self.dfh]) / self.p

    def unseen_algorithm(self, y, p, N, tolerance=1e-5):
        """
        Unseen算法实现，支持对 N 的容差。
        
        参数:
        y: 样本的DFH，格式为字典 {i: y_i}，表示恰好出现i次的不同块的数量。
        p: 样本比例，p = K / N，其中K是样本大小，N是数据集大小。
        N: 数据集的总大小。
        tolerance: 线性规划的容差。
        epsilon: N 的容差范围。
        
        返回:
        x_hat: 估计的数据集DFH。
        r_hat: 估计的去重比例。
        delta_opt: 初始最优解的目标函数值。
        """
        # 过滤掉 y_i = 0 的项
        y_filtered = {i: cnt for i, cnt in y.items() if cnt > 0}
        if not y_filtered:
            raise ValueError("样本 DFH 全为零，无法估计")
        
        max_i = int(max(y_filtered.keys()) / p)
        y_array = np.array([y_filtered.get(i, 0) for i in range(1, max_i + 1)])
        
        # 构建期望DFH矩阵 A_p
        A_p = self.build_expected_matrix(p, max_i)
        
        # 定义线性规划的目标函数和约束条件
        num_vars = max_i  # x'_i 的变量数量
        num_abs_vars = max_i  # u_i 的变量数量
        total_vars = num_vars + num_abs_vars  # 总变量数量
        
        # 目标函数系数
        c = np.zeros(total_vars)
        for i in range(max_i):
            c[num_vars + i] = 1 / np.sqrt(y_array[i] + 1)  # u_i 的系数
        
        # 约束条件矩阵
        A_ub = np.zeros((2 * max_i + 2, total_vars))  # 增加两个不等式约束
        b_ub = np.zeros(2 * max_i + 2)
        
        # 添加 u_i >= y_i - (A_p * x')_i 的约束
        # -A_p * x' - u_i <= -y_i
        for i in range(max_i):
            A_ub[i, :num_vars] = -A_p[i, :]  # -A_p * x'
            A_ub[i, num_vars + i] = -1  # -u_i
            b_ub[i] = -y_array[i]
    
        # 添加 u_i >= (A_p * x')_i - y_i 的约束
        # A_p * x' - u_i <= y_i
        for i in range(max_i):
            A_ub[max_i + i, :num_vars] = A_p[i, :]  # A_p * x'
            A_ub[max_i + i, num_vars + i] = -1  # u_i
            b_ub[max_i + i] = y_array[i]
        
        # 添加 sum(x'_i * i) <= (1 + epsilon) * N 的约束
        A_ub[2 * max_i, :num_vars] = np.arange(1, max_i + 1)
        b_ub[2 * max_i] = (1 + self.epsilon) * N
        
        # 添加 sum(x'_i * i) >= (1 - epsilon) * N 的约束
        # - (1 - epsilon) * N <= - sum(x'_i * i)
        A_ub[2 * max_i + 1, :num_vars] = -np.arange(1, max_i + 1)
        b_ub[2 * max_i + 1] = -(1 - self.epsilon) * N
        
        # 变量边界
        bounds = [(0, None)] * total_vars
        
        # 线性规划求解
        res = linprog(
            c, 
            A_ub=A_ub, 
            b_ub=b_ub, 
            bounds=bounds,
            method='highs',
            options={'tol': tolerance, 'maxiter': self.maxiter}
        )
        
        if res.success:
            x_hat = res.x[:num_vars]
            r_hat = np.sum(x_hat) / N
            delta_opt = res.fun  # 初始最优解的目标函数值
            return x_hat, r_hat, delta_opt, res
        else:
            raise ValueError(f"线性规划求解失败: {res.message}")
        
    def build_expected_matrix(self, p, max_j):
        """
        构建期望DFH矩阵 A_p。
        
        参数:
        p: 样本比例。
        max_j: 数据集中块的最大出现次数。
        
        返回:
        A_p: 期望DFH矩阵，形状为 (max_j, max_j)。
        """
        # 初始化矩阵 A_p
        A_p = np.zeros((max_j, max_j))
        
        # 填充矩阵 A_p
        for i in range(1, max_j + 1):  # 样本中块的出现次数 i
            for j in range(1, max_j + 1):  # 数据集中块的出现次数 j
                if i <= j:
                    A_p[i-1, j-1] = self.binom_pmf(i, j, p)
                else:
                    A_p[i-1, j-1] = 0  # 如果 i > j，概率为 0
        return A_p

    def binom_pmf(self, k, n, p):
        """
        计算二项分布的概率质量函数 (PMF)。
        
        参数:
        k: 成功次数。
        n: 试验次数。
        p: 成功概率。
        
        返回:
        PMF值。
        """
        from scipy.special import comb
        return comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
    
    def delta_p(self, x, y):
        """
        计算目标函数 Delta_p(x, y)。
        
        参数:
        x: 估计的DFH。
        y: 样本的DFH。
        
        返回:
        Delta_p(x, y) 的值。
        """
        y_array = np.array([y.get(i, 0) for i in range(1, len(x) + 1)])
        A_p = self.build_expected_matrix(self.p, len(x))
        return np.sum(np.abs(y_array - A_p @ x) / np.sqrt(y_array + 1))
    
    def unseen_range(self, y, p, N):
        """
        Unseen Range 算法实现，提供去重比例的置信区间。
        
        参数:
        y: 样本的DFH，格式为字典 {i: y_i}。
        p: 样本比例。
        N: 数据集的总大小。
        
        返回:
        r_low: 去重比例的下界。
        r_high: 去重比例的上界。
        """
        # Step 1: 计算初始最优解
        x_opt, r_opt, delta_opt, res = self.unseen_algorithm(y, p, N)
        
        # Step 2: 定义可行区域约束
        tolerance = delta_opt + self.alpha * np.sqrt(delta_opt)

        # 过滤掉 y_i = 0 的项
        y_filtered = {i: cnt for i, cnt in y.items() if cnt > 0}
        if not y_filtered:
            raise ValueError("样本 DFH 全为零，无法估计")
        
        max_i = int(max(y_filtered.keys()) / p)
        y_array = np.array([y_filtered.get(i, 0) for i in range(1, max_i + 1)])
        
        # 构建期望DFH矩阵 A_p
        A_p = self.build_expected_matrix(p, max_i)
        
        # 定义线性规划的目标函数和约束条件
        num_vars = max_i  # x'_i 的变量数量
        num_abs_vars = max_i  # u_i 的变量数量
        total_vars = num_vars + num_abs_vars  # 总变量数量
        
        # 目标函数系数
        c = np.zeros(total_vars)
        for i in range(max_i):
            c[i] = 1  # 最小化sum(x'_i)
        
        # 约束条件矩阵
        A_ub = np.zeros((2 * max_i + 3, total_vars))  # 增加两个不等式约束
        b_ub = np.zeros(2 * max_i + 3)
        
        # 添加 u_i >= y_i - (A_p * x')_i 的约束
        # -A_p * x' - u_i <= -y_i
        for i in range(max_i):
            A_ub[i, :num_vars] = -A_p[i, :]  # -A_p * x'
            A_ub[i, num_vars + i] = -1  # -u_i
            b_ub[i] = -y_array[i]
    
        # 添加 u_i >= (A_p * x')_i - y_i 的约束
        # A_p * x' - u_i <= y_i
        for i in range(max_i):
            A_ub[max_i + i, :num_vars] = A_p[i, :]  # A_p * x'
            A_ub[max_i + i, num_vars + i] = -1  # u_i
            b_ub[max_i + i] = y_array[i]
        
        # 添加 sum(x'_i * i) <= (1 + epsilon) * N 的约束
        A_ub[2 * max_i, :num_vars] = np.arange(1, max_i + 1)
        b_ub[2 * max_i] = (1 + self.epsilon) * N
        
        # 添加 sum(x'_i * i) >= (1 - epsilon) * N 的约束
        # - (1 - epsilon) * N <= - sum(x'_i * i)
        A_ub[2 * max_i + 1, :num_vars] = -np.arange(1, max_i + 1)
        b_ub[2 * max_i + 1] = -(1 - self.epsilon) * N

        # 添加 Δp(x, y) <= Δp_opt + α * sqrt(Δp_opt) 的约束
        # Δp(x, y) = sum(1/sqrt(y_i + 1)) * u_i)
        for i in range(max_i):
            A_ub[2 * max_i + 2, num_vars + i] = 1 / np.sqrt(y_array[i] + 1)  # u_i 的系数
        b_ub[2 * max_i + 2] = tolerance

        # 变量边界
        bounds = [(0, None)] * total_vars
        
        # Step 3: 最小化去重比例
        res_low = linprog(
            c, 
            A_ub=A_ub, 
            b_ub=b_ub, 
            bounds=bounds,
            method='highs',
            options={'tol': tolerance, 'maxiter': self.maxiter}
        )
        if not res_low.success:
            raise ValueError(f"最小化去重比例失败: {res_low.message}")
        r_low = np.sum(res_low.x[:max_i]) / N

        # Step 4: 最大化去重比例
        # 目标函数系数
        c = np.zeros(total_vars)
        for i in range(max_i):
            c[i] = -1  # 最大化sum(x'_i)
        res_max = linprog(
            c, 
            A_ub=A_ub, 
            b_ub=b_ub, 
            bounds=bounds,
            method='highs',
            options={'tol': tolerance, 'maxiter': self.maxiter}
        )
        if not res_max.success:
            raise ValueError(f"最大化去重比例失败: {res_max.message}")
        r_max = np.sum(res_max.x[:max_i]) / N
        
        return r_low, r_max
    
    # 外部调用，直接用dfh估计去重比例
    def estimate_support_size(self, filder_num=100):
        """
        filder_num : 过滤数，小于该值的部分将使用算法估计，大于的部分将使用频率估计

        return : (r_low, r_high)
        """
        # 根据过滤数 filder_num，筛选出符合条件的字典 F
        F = {i: j for i, j in self.dfh if i <= filder_num}
    
        # 计算需要使用算法估计得样本总块数 K_sample
        K_sample = sum(i * j for i, j in F.items())
        N = int(K_sample / self.p)  # 计算原始数据集大小
        
        # 验证样本总块数是否与 p*N 匹配
        assert np.isclose(K_sample, self.p * N, rtol=1e-3), "样本总块数与 p*N 不匹配"
        
        # 计算未见过数据的范围
        r_low, r_high = self.unseen_range(F, self.p, N)
        # 筛选出过滤数大于 filder_num 的字典 dense_dfh
        dense_dfh = {i: j for i, j in self.dfh if i > filder_num}
        # r = ( r_*N + sum(dense_dfh.values()) ) / sum(dfh.values())
        r_low = ( r_low * N + sum(dense_dfh.values()) ) / self.N
        r_high = ( r_high * N + sum(dense_dfh.values()) ) / self.N

        return r_low, r_high

# 示例使用
if __name__ == "__main__":
    # 样本DFH
    data_0201_1041 = [(1, 741937), (2, 80109), (3, 13029), (4, 4630), (5, 1811), (6, 954), 
                      (7, 602), (8, 236), (9, 137), (10, 57), (11, 42), (12, 25), (13, 14), 
                      (14, 12), (15, 18), (16, 13), (17, 9), (18, 4), (19, 3), (20, 1), 
                      (21, 2), (22, 1), (23, 3), (24, 4), (25, 8), (26, 3), (27, 7), 
                      (28, 2), (29, 2), (30, 5), (31, 12), (32, 6), (33, 4), (34, 4), 
                      (35, 3), (36, 2), (37, 2), (38, 3), (39, 1), (41, 3), (42, 4), 
                      (43, 6), (46, 2), (47, 1), (48, 1), (50, 1), (53, 1), (56, 3), 
                      (57, 3), (58, 1), (59, 2), (60, 2), (63, 1), (64, 1), (66, 1), 
                      (68, 1), (69, 1), (70, 1), (71, 2), (72, 1), (74, 1), (75, 1), 
                      (76, 2), (77, 2), (78, 5), (79, 2), (82, 1), (83, 3), (84, 1), 
                      (85, 5), (86, 1), (87, 3), (88, 3), (89, 3), (106, 1), (108, 3), 
                      (109, 1), (110, 1), (113, 1), (115, 2), (116, 1), (120, 2), 
                      (121, 1), (126, 4), (139, 1), (178, 1), (215, 1), (298, 1), 
                      (312, 1), (357, 1), (359, 1), (464, 1), (500, 1), (511, 1), 
                      (551, 1), (711, 1), (891, 1), (87684, 1)]
    
    unseen = Unseen(data_0201_1041, p=0.3, alpha=0.5)
    try:
        r_low, r_high = unseen.estimate_support_size()
        print(f"去重比例的置信区间: [{r_low}, {r_high}]")
    except ValueError as e:
        print(e)