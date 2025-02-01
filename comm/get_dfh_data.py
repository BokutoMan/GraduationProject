import numpy as np

def sparse_to_dense(sparse_matrix):
    # 找到最大行号以确定稠密矩阵的大小
    max_row = max(row for row, _ in sparse_matrix)
    # 初始化稠密矩阵，大小为 (max_row + 1, 1)，填充为0
    dense_matrix = np.zeros((max_row + 1, 1), dtype=int)
    
    # 遍历稀疏矩阵，填充稠密矩阵
    for row, value in sparse_matrix:
        dense_matrix[row - 1, 0] = value  # 行号从1开始，索引从0开始
    
    return dense_matrix


if __name__ == '__main__':
    from data.data01 import data1822
    print(sparse_to_dense(data1822))