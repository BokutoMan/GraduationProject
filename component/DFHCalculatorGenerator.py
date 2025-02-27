from typing import Generator
from utils import Reader, SimpleLogger
from collections import Counter
from comm import hash_mm3_64
from component.HashCount import HashCount
from component.CustomHeap import CustomHeap

class DFHCalculatorGenerator:
    def __init__(self, data :Generator, low_memory_mode=False, max_blocks=None, per_step=None):
        self.data = data
        self.low_memory_mode = low_memory_mode
        self.max_blocks = max_blocks
        self.per_step = per_step
        if low_memory_mode:
            self.generator = self.low_memory_mode_generator()
            self.heap = CustomHeap(max_size=max_blocks)
            assert max_blocks is not None
        else:
            self.generator = self.normal_mode_generator()
            self.hash_of_datas = Counter()
        self.num = 0

    def __iter__(self):
        return self

    def __next__(self):
        next(self.generator)
    
    def set_new_data(self, data):
        self.data = data
        if self.low_memory_mode:
            self.generator = self.low_memory_mode_generator()
        else:
            self.generator = self.normal_mode_generator()

    def get_result(self):
        if self.low_memory_mode:
            # 统计哈希频率直方图
            histogram_data = Counter([hc.count for hc in self.heap])
            histogram_data = list(histogram_data.items())  # 转换为列表
            histogram_data.sort()  # 按频率排序

            return histogram_data
        else:
             # 统计哈希频率直方图
            histogram_data = Counter(self.hash_of_datas.values())
            histogram_data = list(histogram_data.items())  # 转换为列表
            histogram_data.sort()  # 按频率排序

            return histogram_data
    
    def low_memory_mode_generator(self):
        # 遍历数据块，计算哈希并记录
        for data in self.data:
            hash_of_data = hash_mm3_64(data)  # 计算哈希值
            self.heap.push(HashCount(hash_of_data, 1))  # 将哈希值推入堆中
            self.num += 1
            if self.per_step is not None:
                if self.num % self.per_step == 0:
                    SimpleLogger.memory_log(f"第 {self.num} 个哈希块计算中")
                    yield
    def normal_mode_generator(self):
        # 遍历数据块，计算哈希并统计频率
        for data in self.data:
            hash_of_data = hash_mm3_64(data)  # 计算哈希值
            self.hash_of_datas.update([hash_of_data])  # 统计哈希值出现次数
            self.num += 1
            if self.per_step is not None:
                if self.num % self.per_step == 0:
                    SimpleLogger.memory_log(f"第 {self.num} 个哈希块计算中")
                    yield


# 使用函数
if __name__ == "__main__":
    from comm import timer_decorator
    @timer_decorator("main函数: 常规模式")
    def main1():
        reader = Reader.get_test_reader().get_reader()
        dfh_calculator = DFHCalculatorGenerator(reader, low_memory_mode=False, per_step=100000)
        for _ in dfh_calculator:
            SimpleLogger.memory_log(f"第 {dfh_calculator.num} 个哈希块计算中")
        print(dfh_calculator.get_result())

    @timer_decorator("main函数: 低内存模式")
    def main2():
        reader = Reader.get_test_reader().get_reader(new=True)
        dfh_calculator = DFHCalculatorGenerator(reader, low_memory_mode=True, max_blocks=1000000, per_step=100000)
        for _ in dfh_calculator:
            SimpleLogger.memory_log(f"第 {dfh_calculator.num} 个哈希块计算中")
        print(dfh_calculator.get_result())
    
    main2()