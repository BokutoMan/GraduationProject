import numpy as np
import yaml

def generate_random_positive_integer_vector(D, max):
    # 初始化向量
    y = np.zeros(D, dtype=int)
    
    # 随机生成D个正整数
    for i in range(D):
        y[i] = np.random.randint(0, max)
   
    return y

if __name__=="__main__":
    # 测试函数
    y =generate_random_positive_integer_vector(50, 50)
    y[0] = 500
    y = list(y)
    y.sort(reverse=True)
    print(y)
