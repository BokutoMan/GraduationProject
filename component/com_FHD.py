from utils import Reader, SimpleLogger
import mmh3
from collections import Counter

def hash_mm3_64(data, re_float=True):
    # 使用MurmurHash3的64位版本
    hash_value = mmh3.hash64(data)[0]
    # 将64位哈希值映射到0-1范围
    if re_float:
        return hash_value / 2**64
    return hash_value

datas = Reader.get_reader()
hash_of_datas = Counter()
num = 0
for data in datas:
    hash_of_data = hash_mm3_64(data)
    hash_of_datas.update([hash_of_data])
    num += 1
    print(f"\r 第 {num} 个哈希块计算中", end=" ")
print(f"\r 哈希块计算完成, 一共{num}个")

Histogram_data_of_hashs = Counter(hash_of_datas.values())

Histogram_data_of_hashs = list(Histogram_data_of_hashs.items())

Histogram_data_of_hashs.sort(key= lambda x:x[1])

print(Histogram_data_of_hashs)


