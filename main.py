from utils import *
import hashlib
import concurrent.futures
from collections import Counter
import matplotlib.pyplot as plt
from comm import timer_decorator

# 假设 data_blocks 是一个生成器，它逐个产生数据块
def hash_data_block(block):
    return hashlib.sha256(block).hexdigest()

# def compute_hashes(data_blocks):
#     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#         # 使用 map 来并行计算哈希值
#         hash_values = list(executor.map(hash_data_block, data_blocks))
#     return hash_values
logger = SimpleLogger.get_logger()
@timer_decorator
def go():
    # 计算哈希值并统计频率
    data_blocks = Reader.get_reader()
    # hash_values = compute_hashes(data_blocks)
    hash_counts = Counter()
    i = 0
    for block in data_blocks:
        i += 1
        hash_counts.update([hash_data_block(block),])
        if i % 1000 == 0:
            logger.memory_log()
        print(f"\r 正在计算第 {i} 个 hash ", end=" ")
    print()
    return hash_counts
hash_counts = go()
# 使用 hash_counts 来生成直方图
# 过滤出出现次数大于1的数据
filtered_hash_counts = {k: v for k, v in hash_counts.items() if v > 1}
print(filtered_hash_counts.values())
# 准备直方图数据
frequencies = list(filtered_hash_counts.values())
labels = [i for i in range(len(frequencies))]

# 生成直方图
plt.bar(labels, frequencies)
plt.xlabel('Hash Prefixes')
plt.ylabel('Frequency')
plt.title('Frequency Distribution Histogram of Hash Prefixes')
plt.show()
