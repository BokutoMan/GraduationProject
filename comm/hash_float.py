import mmh3


def hash_mm3_64(data, re_float=True):
    """
    使用 MurmurHash3 的 64 位版本，将哈希值映射到 [0, 1] 范围。
    
    :param data: 要哈希的字符串。
    :param re_float: 是否返回浮点数形式（归一化到 [0, 1]）。
    :return: 归一化的哈希值或原始哈希值。
    """
    hash_value = mmh3.hash64(data)[0]
    if re_float:
        return abs(hash_value / 2**63)
    return hash_value


if __name__=="__main__":
    from collections import Counter
    count = Counter()
    for i in range(1000000):
        s = f"杨利伟的毕业设计{i}"
        num = hash_mm3_64(s)
        num = int(num*10)
        count.update([num])
    print(count.items())