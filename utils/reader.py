import os
import random

def read_random_blocks(file_path, block_size=1024, percentage=15):
    """
    从大文件中随机读取一定比例的块。

    :param file_path: 文件路径。
    :param block_size: 每个块的大小（以字节为单位），默认为1MB。
    :param percentage: 要读取的块的比例（例如，15表示15%）。
    """
    file_size = os.path.getsize(file_path)
    num_blocks = (file_size + block_size - 1) // block_size  # 计算总块数
    num_blocks_to_read = int(num_blocks * (percentage / 100))  # 计算要读取的块数

    # 随机选择要读取的块索引
    blocks_to_read = random.sample(range(num_blocks), num_blocks_to_read)

    with open(file_path, 'rb') as file:
        for block_index in blocks_to_read:
            # 计算当前块的起始位置
            start_pos = block_index * block_size
            file.seek(start_pos)

            # 读取当前块的数据
            block_data = file.read(block_size)
            yield block_data

# 使用示例
file_path = 'path_to_your_large_file'
percentage_to_read = 15  # 可以调节这个值

for block_data in read_random_blocks(file_path, percentage=percentage_to_read):
    # 处理每个读取的块
    print(block_data)  # 假设你有一个处理块的函数
