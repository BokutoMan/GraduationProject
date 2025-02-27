from typing import Generator
from utils import Reader, SimpleLogger
from collections import Counter
from comm import hash_mm3_64
from component.HashCount import HashCount
from component.CustomHeap import CustomHeap


def compute_dfh(datas, max_blocks=None, print_interval=None):
    """
    计算数据频率直方图（DFH）。

    :param datas: 数据块迭代器。
    :param log_interval: 每隔多少个块记录一次内存日志。
    :param max_blocks: 低内存模式下，限制要统计的最大块数。如果为 None，则统计所有数据块。
    :return: 排序后的直方图数据，格式为 [(频率, 出现次数), ...]。
    """
    num = 0
    # 创建一个最大堆来跟踪哈希值
    heap = CustomHeap()

    # 遍历数据块，计算哈希并记录
    for data in datas:
        hash_of_data = hash_mm3_64(data)  # 计算哈希值
        heap.push(HashCount(hash_of_data, 1))  # 将哈希值推入堆中
        num += 1

        # 实时打印进度
        if print_interval is not None:
            if num % print_interval == 0:
                print(f"\r 第 {num} 个哈希块计算中", end=" ")

        # 如果堆的大小超过 max_blocks，删除最小的元素
        if max_blocks is not None:
            if len(heap) > max_blocks:
                heap.pop()
        if num % 100000 == 0:
                SimpleLogger.memory_log(f"第 {num} 个哈希块计算中")

    # 打印完成信息
    print(f"\r 哈希块计算完成, 一共 {num} 个")


    # 统计哈希频率直方图
    histogram_data = Counter([hc.count for hc in heap])
    histogram_data = list(histogram_data.items())  # 转换为列表
    histogram_data.sort()  # 按频率排序

    return histogram_data

def compute_dfh_use_counter(datas, print_interval=None):
    """
    计算数据频率直方图（DFH）。

    :param datas: 数据块迭代器。
    :param log_interval: 每隔多少个块记录一次内存日志。
    :return: 排序后的直方图数据，格式为 [(频率, 出现次数), ...]。
    """
    hash_of_datas = Counter()
    num = 0

    # 遍历数据块，计算哈希并统计频率
    for data in datas:
        hash_of_data = hash_mm3_64(data)  # 计算哈希值
        hash_of_datas.update([hash_of_data])  # 统计哈希值出现次数
        num += 1

        if print_interval is not None:
            if num % print_interval == 0:
                print(f"\r 第 {num} 个哈希块计算中", end=" ")
        
        if num % 100000 == 0:
            SimpleLogger.memory_log(f"第 {num} 个哈希块计算中")

    # 打印完成信息
    print(f"\r 哈希块计算完成, 一共 {num} 个")

    # 统计哈希频率直方图
    histogram_data = Counter(hash_of_datas.values())
    histogram_data = list(histogram_data.items())  # 转换为列表
    histogram_data.sort()  # 按频率排序

    return histogram_data


# 使用函数
if __name__ == "__main__":
    from comm import timer_decorator
    @timer_decorator("main函数: 常规模式")
    def main1():
        datas = Reader.get_test_reader().get_reader(new=True)  # 获取数据块迭代器
        dfh = compute_dfh(datas, max_blocks=None)  # 计算 DFH
        print(dfh)  # 输出直方图

    @timer_decorator("main函数: 低内存模式")
    def main2():
        datas = Reader.get_test_reader().get_reader(new=True)  # 获取数据块迭代器
        max_blocks = 500000  # 低内存模式下最大块数，设置为 None 代表常规模式
        dfh = compute_dfh(datas, max_blocks=max_blocks)  # 计算 DFH
        print(dfh)  # 输出直方图

    @timer_decorator("main函数: 使用counter统计频率")
    def main3():
        datas = Reader.get_test_reader().get_reader(new=True)  # 获取数据块迭代器
        dfh = compute_dfh_use_counter(datas)  # 计算 DFH
        print(dfh)  # 输出直方图
    main1()
    main2()
    main3()