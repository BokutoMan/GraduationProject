from utils import Reader, SimpleLogger
from collections import Counter
from comm import hash_mm3_64

def compute_dfh(datas, log_interval=10000):
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
    dfh = compute_dfh(datas)  # 计算 DFH
    print(dfh)  # 输出直方图
