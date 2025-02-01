import numpy as np
from scipy.stats import entropy

# 计算“指纹”函数
def makeFinger(v):
    # 计算v的直方图，得到每个值的频次
    h1, bins = np.histogram(v, bins=np.arange(np.min(v), np.max(v) + 2))
    
    # 计算频次的直方图，即每个频次出现的次数
    f, _ = np.histogram(h1, bins=np.arange(0, np.max(h1) + 2))
    
    # 去掉出现次数为0的部分
    f = f[1:]
    
    return f

if __name__ == "__main__":
    # 生成一个随机样本并计算其指纹
    n = 20  # 支持集大小
    k = 10000  # 样本大小
    samp = np.random.randint(1, n + 1, k)  # 从1到n生成随机整数

    # 计算样本的指纹
    f = makeFinger(samp)

    # 熵的估计
    # 真实分布的熵（均匀分布）
    trueEntropy = np.log(n)

    # 样本的经验熵计算
    probabilities = (np.arange(1, len(f) + 1) / k)  # 概率分布
    empiricalEntropy = -np.dot(f, np.log(probabilities)) + np.sum(f) / (2 * k)

    # 恢复的直方图的熵估计
    h, x = np.histogram(f, bins=np.arange(1, np.max(f) + 2))
    estimatedEntropy = -np.sum(h * (x[:-1] * np.log(x[:-1] + 1e-10)))  # 加一个小值避免log(0)

    # 恢复的分布的支持集大小
    suppSz = np.sum(h)

    # 输出结果
    print(f"True Entropy: {trueEntropy}")
    print(f"Empirical Entropy: {empiricalEntropy}")
    print(f"Estimated Entropy: {estimatedEntropy}")
    print(f"Support Size: {suppSz}")
