from utils import Reader, SimpleLogger
from collections import Counter
from comm import hash_mm3_64
from component.HashCount import HashCount
from component.CustomHeap import CustomHeap

def compute_dfh(datas, log_interval=10000, max_blocks=None):
    """
    计算数据频率直方图（DFH）。

    :param datas: 数据块迭代器。
    :param log_interval: 每隔多少个块记录一次内存日志。
    :param max_blocks: 低内存模式下，限制要统计的最大块数。如果为 None，则统计所有数据块。
    :return: 排序后的直方图数据，格式为 [(频率, 出现次数), ...]。
    """
    hash_of_datas = Counter()
    num = 0

    if max_blocks is not None:
        # 低内存模式：只统计哈希值最大的部分
        # 创建一个最大堆来跟踪哈希值
        heap = CustomHeap()

        # 遍历数据块，计算哈希并记录
        for data in datas:
            hash_of_data = hash_mm3_64(data)  # 计算哈希值
            heap.push(HashCount(hash_of_data, 1))  # 将哈希值推入堆中
            num += 1

            # 实时打印进度
            print(f"\r 第 {num} 个哈希块计算中", end=" ")

            # 每隔 log_interval 记录一次内存状态
            if num % log_interval == 0:
                SimpleLogger.memory_log()

            # 如果堆的大小超过 max_blocks，删除最小的元素
            if len(heap) > max_blocks:
                heap.pop()

        # 打印完成信息
        print(f"\r 哈希块计算完成, 一共 {num} 个")

        # 统计哈希频率直方图
        for hash_of_data in heap:
            hash_of_datas.update([hash_of_data.count])

    else:
        # 常规模式：统计所有内存块
        # 遍历数据块，计算哈希并统计频率
        for data in datas:
            hash_of_data = hash_mm3_64(data)  # 计算哈希值
            heap.push(HashCount(hash_of_data, 1))  # 将哈希值推入堆中
            num += 1

            # 实时打印进度
            print(f"\r 第 {num} 个哈希块计算中", end=" ")

            # 每隔 log_interval 记录一次内存状态
            if num % log_interval == 0:
                SimpleLogger.memory_log()

        # 打印完成信息
        print(f"\r 哈希块计算完成, 一共 {num} 个")

    # 统计哈希频率直方图
    histogram_data = Counter(hash_of_datas.values())
    histogram_data = list(histogram_data.items())  # 转换为列表
    histogram_data.sort()  # 按频率排序

    return histogram_data


# 使用函数
if __name__ == "__main__":
    datas = Reader.get_reader()  # 获取数据块迭代器
    max_blocks = 10000  # 低内存模式下最大块数，设置为 None 代表常规模式
    dfh = compute_dfh(datas, log_interval=10000, max_blocks=max_blocks)  # 计算 DFH
    print(dfh)  # 输出直方图
